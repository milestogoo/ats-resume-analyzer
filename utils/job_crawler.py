import requests
from typing import List, Dict
import json
from datetime import datetime, timedelta
import time
import os
from bs4 import BeautifulSoup
import urllib.parse

class JobCrawler:
    def __init__(self):
        self.base_urls = {
            'indeed': 'https://api.indeed.com/ads/apisearch',
            'naukri': 'https://www.naukri.com/jobapi/v3/search',
            'linkedin': 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
        }

        # Headers for different sites
        self.headers = {
            'indeed': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'naukri': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'appid': 109,
                'systemid': 109
            },
            'linkedin': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

    def search_jobs(self, keywords: List[str], location: str = '') -> List[Dict]:
        """
        Search for jobs across multiple platforms
        Returns aggregated job listings
        """
        all_jobs = []

        for keyword in keywords:
            # Add delay between requests
            time.sleep(1)

            try:
                # Indeed Jobs
                indeed_jobs = self._search_indeed_jobs(keyword, location)
                all_jobs.extend(indeed_jobs)

                # Naukri Jobs
                naukri_jobs = self._search_naukri_jobs(keyword, location)
                all_jobs.extend(naukri_jobs)

                # LinkedIn Jobs
                linkedin_jobs = self._search_linkedin_jobs(keyword, location)
                all_jobs.extend(linkedin_jobs)

            except Exception as e:
                print(f"Error searching for {keyword}: {str(e)}")
                continue

        # Remove duplicates and sort by date
        unique_jobs = self._deduplicate_jobs(all_jobs)
        sorted_jobs = sorted(unique_jobs, 
                           key=lambda x: x.get('posted_date', ''), 
                           reverse=True)

        return sorted_jobs[:50]  # Return top 50 most recent jobs

    def _search_indeed_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Search Indeed Jobs"""
        try:
            params = {
                'q': keyword,
                'l': location,
                'format': 'json',
                'limit': 25,
                'fromage': 30,  # Last 30 days
                'sort': 'date'
            }

            response = requests.get(
                'https://api.indeed.com/v2/search',
                params=params,
                headers=self.headers['indeed']
            )

            if response.status_code == 200:
                jobs = response.json().get('results', [])
                return [{
                    'title': job['title'],
                    'company': job['company'],
                    'location': job.get('location', 'Not specified'),
                    'url': job['url'],
                    'posted_date': job.get('date', ''),
                    'source': 'Indeed',
                    'description': job.get('snippet', '')[:200] + '...'
                } for job in jobs]

        except Exception as e:
            print(f"Indeed Jobs API error: {str(e)}")
        return []

    def _search_naukri_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Search Naukri Jobs"""
        try:
            params = {
                'noOfResults': 25,
                'urlType': 'search_by_keyword',
                'searchType': 'adv',
                'keyword': keyword,
                'location': location,
                'sort': 'r'  # Sort by relevance
            }

            response = requests.get(
                self.base_urls['naukri'],
                params=params,
                headers=self.headers['naukri']
            )

            if response.status_code == 200:
                jobs = response.json().get('jobDetails', [])
                return [{
                    'title': job['title'],
                    'company': job['companyName'],
                    'location': job.get('location', 'Not specified'),
                    'url': job['jobUrl'],
                    'posted_date': job.get('createdDate', ''),
                    'source': 'Naukri',
                    'description': job.get('jobDescription', '')[:200] + '...'
                } for job in jobs]

        except Exception as e:
            print(f"Naukri Jobs API error: {str(e)}")
        return []

    def _search_linkedin_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Search LinkedIn Jobs"""
        try:
            encoded_keyword = urllib.parse.quote(keyword)
            encoded_location = urllib.parse.quote(location) if location else ''

            url = f"https://www.linkedin.com/jobs/search?keywords={encoded_keyword}&location={encoded_location}"
            response = requests.get(url, headers=self.headers['linkedin'])

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')

                jobs = []
                for card in job_cards:
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

                return jobs[:25]  # Return top 25 results

        except Exception as e:
            print(f"LinkedIn Jobs API error: {str(e)}")
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
        """
        Format jobs by category for display
        Returns dict with jobs grouped by category
        """
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
        """
        Filter jobs based on posting date
        """
        if filter_period == 'all':
            return jobs

        today = datetime.now()
        filtered_jobs = []

        for job in jobs:
            try:
                # Parse the job's posted date
                posted_date = datetime.strptime(job['posted_date'], '%Y-%m-%d')

                # Calculate days difference
                days_old = (today - posted_date).days

                # Apply filter based on period
                if (filter_period == 'today' and days_old == 0) or \
                   (filter_period == '3days' and days_old <= 3) or \
                   (filter_period == '7days' and days_old <= 7) or \
                   (filter_period == '21days' and days_old <= 21):
                    filtered_jobs.append(job)
            except Exception as e:
                print(f"Error parsing date for job: {str(e)}")
                # Include jobs with unparseable dates in all results
                if filter_period == 'all':
                    filtered_jobs.append(job)

        return filtered_jobs