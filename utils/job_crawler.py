import requests
import re
from typing import List, Dict
from datetime import datetime, timedelta
import time
import os
from bs4 import BeautifulSoup
import urllib.parse

class JobCrawler:
    def __init__(self):
        self.base_urls = {
            'indeed': 'https://www.indeed.com/jobs',
            'naukri': 'https://www.naukri.com/jobs',
            'linkedin': 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
        }

        # Experience level mappings
        self.experience_ranges = {
            'entry': (0, 2),
            'mid': (2, 5),
            'senior': (5, 8),
            'lead': (8, 12),
            'director': (12, float('inf'))
        }

        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def detect_experience_level(self, title: str, description: str) -> str:
        """Detect experience level from job title and description"""
        text = f"{title} {description}".lower()

        # Keywords indicating experience level
        level_indicators = {
            'director': ['director', 'vp', 'head of', 'chief'],
            'lead': ['lead', 'principal', 'architect', 'manager'],
            'senior': ['senior', 'sr.', 'experienced'],
            'mid': ['mid level', 'mid-level', 'intermediate'],
            'entry': ['entry level', 'junior', 'graduate', 'fresher']
        }

        # Check for explicit experience requirements
        exp_pattern = r'(\d+)[\+\-]?\s*(?:to\s*(\d+))?\s*(?:years?|yrs?)'
        exp_match = re.search(exp_pattern, text)
        if exp_match:
            min_exp = int(exp_match.group(1))
            if min_exp >= 12:
                return 'director'
            elif min_exp >= 8:
                return 'lead'
            elif min_exp >= 5:
                return 'senior'
            elif min_exp >= 2:
                return 'mid'
            return 'entry'

        # Check for level indicators in text
        for level, keywords in level_indicators.items():
            if any(keyword in text for keyword in keywords):
                return level

        return 'mid'  # Default to mid-level if no clear indicators

    def search_jobs(self, keywords: List[str], location: str = '', experience_level: str = None) -> List[Dict]:
        """Search for jobs across multiple platforms"""
        all_jobs = []

        for keyword in keywords:
            try:
                # LinkedIn Jobs (most reliable API)
                linkedin_jobs = self._search_linkedin_jobs(keyword, location)
                all_jobs.extend(linkedin_jobs)

                # Use web scraping for Indeed and Naukri as fallback
                try:
                    indeed_jobs = self._scrape_indeed_jobs(keyword, location)
                    all_jobs.extend(indeed_jobs)
                except Exception as e:
                    print(f"Indeed scraping error: {str(e)}")

                try:
                    naukri_jobs = self._scrape_naukri_jobs(keyword, location)
                    all_jobs.extend(naukri_jobs)
                except Exception as e:
                    print(f"Naukri scraping error: {str(e)}")

            except Exception as e:
                print(f"Error searching for {keyword}: {str(e)}")
                continue

            time.sleep(1)  # Respect rate limits

        # Add experience level to each job
        for job in all_jobs:
            job['experience_level'] = self.detect_experience_level(job['title'], job['description'])

        # Filter by experience level if specified
        if experience_level:
            all_jobs = [job for job in all_jobs if job['experience_level'] == experience_level]

        # Remove duplicates and sort by date
        unique_jobs = self._deduplicate_jobs(all_jobs)
        sorted_jobs = sorted(unique_jobs, 
                          key=lambda x: x.get('posted_date', ''), 
                          reverse=True)

        return sorted_jobs[:50]  # Return top 50 most recent jobs

    def _scrape_indeed_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Scrape Indeed jobs using web scraping"""
        jobs = []
        encoded_keyword = urllib.parse.quote(keyword)
        encoded_location = urllib.parse.quote(location)

        url = f"https://www.indeed.com/jobs?q={encoded_keyword}&l={encoded_location}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='job_seen_beacon')

            for card in job_cards[:10]:  # Limit to 10 jobs per search
                try:
                    title = card.find('h2', class_='jobTitle').text.strip()
                    company = card.find('span', class_='companyName').text.strip()
                    location = card.find('div', class_='companyLocation').text.strip()
                    description = card.find('div', class_='job-snippet').text.strip()

                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description[:200] + '...',
                        'url': 'https://www.indeed.com' + card.find('a')['href'],
                        'source': 'Indeed',
                        'posted_date': datetime.now().strftime('%Y-%m-%d')
                    })
                except Exception as e:
                    print(f"Error parsing Indeed job card: {str(e)}")
                    continue

        return jobs

    def _scrape_naukri_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Scrape Naukri jobs using web scraping"""
        jobs = []
        encoded_keyword = urllib.parse.quote(keyword)
        encoded_location = urllib.parse.quote(location)

        url = f"https://www.naukri.com/{encoded_keyword}-jobs-in-{encoded_location}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('article', class_='jobTuple')

            for card in job_cards[:10]:  # Limit to 10 jobs per search
                try:
                    title = card.find('a', class_='title').text.strip()
                    company = card.find('a', class_='subTitle').text.strip()
                    location = card.find('li', class_='location').text.strip()
                    description = card.find('div', class_='job-description').text.strip()

                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description[:200] + '...',
                        'url': card.find('a', class_='title')['href'],
                        'source': 'Naukri',
                        'posted_date': datetime.now().strftime('%Y-%m-%d')
                    })
                except Exception as e:
                    print(f"Error parsing Naukri job card: {str(e)}")
                    continue

        return jobs

    def _search_linkedin_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Search LinkedIn Jobs"""
        try:
            encoded_keyword = urllib.parse.quote(keyword)
            encoded_location = urllib.parse.quote(location) if location else ''

            url = f"https://www.linkedin.com/jobs/search?keywords={encoded_keyword}&location={encoded_location}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')

                jobs = []
                for card in job_cards[:10]:  # Limit to 10 jobs per search
                    try:
                        title = card.find('h3', class_='base-search-card__title').text.strip()
                        company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                        location = card.find('span', class_='job-search-card__location').text.strip()
                        job_url = card.find('a', class_='base-card__full-link')['href']

                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location,
                            'url': job_url,
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'LinkedIn',
                            'description': 'Click to view full job details...'
                        })
                    except Exception as e:
                        print(f"Error parsing LinkedIn job card: {str(e)}")
                        continue

                return jobs

        except Exception as e:
            print(f"LinkedIn Jobs error: {str(e)}")
        return []

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate job listings based on title and company"""
        seen = set()
        unique_jobs = []

        for job in jobs:
            key = f"{job['title']}:{job['company']}:{job['location']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs

    def format_jobs_for_display(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """Format jobs by category for display"""
        categorized = {
            'engineering': [],
            'management': [],
            'data': [],
            'design': [],
            'operations': []
        }

        for job in jobs:
            title = job['title'].lower()

            # Categorize based on job title
            if any(keyword in title for keyword in ['engineer', 'developer', 'architect']):
                categorized['engineering'].append(job)
            elif any(keyword in title for keyword in ['manager', 'director', 'lead']):
                categorized['management'].append(job)
            elif any(keyword in title for keyword in ['data', 'machine learning', 'ai']):
                categorized['data'].append(job)
            elif any(keyword in title for keyword in ['designer', 'design']):
                categorized['design'].append(job)
            else:
                categorized['operations'].append(job)

        return categorized

    def filter_jobs_by_date(self, jobs: List[Dict], filter_period: str) -> List[Dict]:
        """Filter jobs based on posting date"""
        if filter_period == 'all':
            return jobs

        today = datetime.now()
        filtered_jobs = []

        for job in jobs:
            try:
                posted_date = datetime.strptime(job['posted_date'], '%Y-%m-%d')
                days_old = (today - posted_date).days

                if (filter_period == 'today' and days_old == 0) or \
                   (filter_period == '3days' and days_old <= 3) or \
                   (filter_period == '7days' and days_old <= 7) or \
                   (filter_period == '21days' and days_old <= 21):
                    filtered_jobs.append(job)
            except Exception as e:
                print(f"Error parsing date for job: {str(e)}")
                if filter_period == 'all':
                    filtered_jobs.append(job)

        return filtered_jobs