import requests
from typing import List, Dict
import json
from datetime import datetime, timedelta
import time

class JobCrawler:
    def __init__(self):
        self.base_urls = {
            'github': 'https://jobs.github.com/positions.json',
            'linkedin': 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
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
                # GitHub Jobs
                github_jobs = self._search_github_jobs(keyword, location)
                all_jobs.extend(github_jobs)
                
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

    def _search_github_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Search GitHub Jobs"""
        try:
            params = {
                'description': keyword,
                'location': location
            }
            response = requests.get(self.base_urls['github'], params=params)
            if response.status_code == 200:
                jobs = response.json()
                return [{
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'url': job['url'],
                    'posted_date': job['created_at'],
                    'source': 'GitHub',
                    'description': job['description'][:200] + '...'  # Truncate description
                } for job in jobs]
        except Exception as e:
            print(f"GitHub Jobs API error: {str(e)}")
        return []

    def _search_linkedin_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Search LinkedIn Jobs"""
        try:
            params = {
                'keywords': keyword,
                'location': location,
                'start': 0
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.base_urls['linkedin'], 
                                 params=params, 
                                 headers=headers)
            
            if response.status_code == 200:
                # Parse LinkedIn's HTML response (simplified)
                jobs = self._parse_linkedin_response(response.text)
                return jobs
        except Exception as e:
            print(f"LinkedIn Jobs API error: {str(e)}")
        return []

    def _parse_linkedin_response(self, html_content: str) -> List[Dict]:
        """Parse LinkedIn jobs from HTML response"""
        # This is a simplified parser - would need more robust HTML parsing
        jobs = []
        # Add actual parsing logic here
        return jobs

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
