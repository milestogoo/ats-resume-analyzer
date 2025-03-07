import re
import nltk
from typing import List, Dict

class RoleExtractor:
    def __init__(self):
        self.common_roles = {
            'engineering': [
                'Software Engineer', 'Senior Software Engineer', 'Engineering Manager',
                'DevOps Engineer', 'Systems Engineer', 'Frontend Engineer',
                'Backend Engineer', 'Full Stack Engineer', 'Site Reliability Engineer',
                'QA Engineer', 'Test Engineer', 'Technical Lead'
            ],
            'management': [
                'Director', 'CTO', 'VP of Engineering', 'Technical Director',
                'Project Manager', 'Product Manager', 'Program Manager',
                'Engineering Director', 'Development Manager'
            ],
            'data': [
                'Data Scientist', 'Data Engineer', 'Machine Learning Engineer',
                'AI Engineer', 'Data Analyst', 'Business Intelligence Analyst'
            ],
            'design': [
                'UX Designer', 'UI Designer', 'Product Designer',
                'Visual Designer', 'Interaction Designer'
            ],
            'operations': [
                'Operations Manager', 'Technical Operations',
                'IT Manager', 'System Administrator'
            ]
        }

        # Flatten roles for easy searching
        self.all_roles = [role.lower() for category in self.common_roles.values()
                         for role in category]

    def extract_roles(self, text: str) -> List[Dict[str, str]]:
        """
        Extract job roles from resume text with experience levels and recency
        """
        found_roles = []
        text_lower = text.lower()

        # Look for dates near role mentions to determine recency
        date_pattern = r'(\d{4})\s*(?:-|to|–|present|current)'
        dates = re.finditer(date_pattern, text)
        current_year = 2025

        # Store positions with their dates
        dated_positions = []
        for date_match in dates:
            year = int(date_match.group(1))
            context_start = max(0, date_match.start() - 150)
            context_end = min(len(text), date_match.start() + 150)
            context = text[context_start:context_end].lower()

            for category, roles in self.common_roles.items():
                for role in roles:
                    role_lower = role.lower()
                    if role_lower in context:
                        dated_positions.append({
                            'role': role,
                            'year': year,
                            'category': category,
                            'is_current': 'present' in context or 'current' in context,
                            'relevance_score': self._calculate_relevance(role_lower, context)
                        })

        # Sort positions by recency and relevance
        dated_positions.sort(key=lambda x: (x['is_current'], x['year'], x['relevance_score']), reverse=True)

        # Take only the most recent and relevant roles (max 3)
        processed_roles = set()
        for position in dated_positions[:5]:  # Consider top 5 positions
            if len(found_roles) >= 3:  # Limit to 3 roles
                break

            role = position['role']
            if role.lower() not in processed_roles:
                exp_level = self._get_experience_level(text_lower, role.lower())
                found_roles.append({
                    'role': role,
                    'category': position['category'],
                    'experience_level': exp_level,
                    'is_current': position['is_current'],
                    'year': position['year']
                })
                processed_roles.add(role.lower())

        return found_roles

    def _get_experience_level(self, text: str, role: str) -> str:
        """Determine experience level for a role based on context"""
        # Find the context around the role mention
        role_index = text.find(role)
        if role_index == -1:
            return 'mid'  # Default if role not found

        # Look for experience indicators in surrounding text
        context_start = max(0, role_index - 100)
        context_end = min(len(text), role_index + 100)
        context = text[context_start:context_end]

        # Check for years of experience
        year_pattern = r'(\d+)[\+\-]?\s*(?:to\s*(\d+))?\s*(?:years?|yrs?)'
        year_match = re.search(year_pattern, context)
        if year_match:
            years = int(year_match.group(1))
            if years >= 12:
                return 'director'
            elif years >= 8:
                return 'lead'
            elif years >= 5:
                return 'senior'
            elif years >= 2:
                return 'mid'
            return 'entry'

        # Check for level indicators
        if any(word in context for word in ['senior', 'sr.', 'lead', 'principal']):
            return 'senior'
        elif any(word in context for word in ['manager', 'director', 'head']):
            return 'lead'
        elif any(word in context for word in ['junior', 'jr.', 'entry', 'associate']):
            return 'entry'

        return 'mid'  # Default to mid-level

    def _categorize_role(self, role: str) -> str:
        """Categorize a role based on keywords"""
        role_lower = role.lower()

        if any(keyword in role_lower for keyword in ['engineer', 'developer', 'architect']):
            return 'engineering'
        elif any(keyword in role_lower for keyword in ['manager', 'director', 'lead']):
            return 'management'
        elif any(keyword in role_lower for keyword in ['data', 'machine learning', 'ai']):
            return 'data'
        elif any(keyword in role_lower for keyword in ['designer', 'design']):
            return 'design'
        else:
            return 'operations'

    def get_search_keywords(self, roles: List[Dict[str, str]]) -> List[str]:
        """Generate search keywords from extracted roles"""
        keywords = []
        for role_info in roles:
            role = role_info['role']
            experience_level = role_info.get('experience_level', 'mid')

            # Add variations based on experience level
            if experience_level == 'senior':
                keywords.extend([
                    f"Senior {role}",
                    f"Lead {role}",
                    role
                ])
            elif experience_level == 'lead':
                keywords.extend([
                    f"Lead {role}",
                    f"Manager {role}",
                    f"Senior {role}"
                ])
            elif experience_level == 'director':
                keywords.extend([
                    f"Director of {role}",
                    f"Head of {role}",
                    f"Senior Manager {role}"
                ])
            else:
                keywords.append(role)

            # Add core role variations
            words = role.split()
            if len(words) > 1:
                if words[0].lower() in ['senior', 'lead', 'principal', 'staff']:
                    keywords.append(' '.join(words[1:]))

                # Add core role
                if 'engineer' in role.lower():
                    keywords.append('Software Engineer')
                elif 'manager' in role.lower():
                    keywords.append('Engineering Manager')

        return list(set(keywords))  # Remove duplicates

    def _calculate_relevance(self, role: str, context: str) -> float:
        """Calculate role relevance based on technical keywords and context"""
        relevance_score = 0.0

        # Modern technical keywords that indicate current relevance
        tech_keywords = [
            'cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'docker',
            'react', 'vue', 'angular', 'node.js', 'python', 'golang',
            'machine learning', 'ai', 'data science', 'devops', 'mlops',
            'microservices', 'serverless', 'full stack', 'blockchain'
        ]

        # Check for technical keywords in context
        for keyword in tech_keywords:
            if keyword in context:
                relevance_score += 1.0

        # Additional points for leadership roles
        if any(word in role for word in ['lead', 'senior', 'architect', 'manager']):
            relevance_score += 0.5

        return relevance_score