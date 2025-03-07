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
        Extract job roles from resume text
        Returns list of roles with their categories
        """
        found_roles = []
        text_lower = text.lower()
        
        # Look for exact matches first
        for category, roles in self.common_roles.items():
            for role in roles:
                role_lower = role.lower()
                if role_lower in text_lower:
                    found_roles.append({
                        'role': role,
                        'category': category,
                        'match_type': 'exact'
                    })

        # Look for partial matches using regex patterns
        role_patterns = [
            r'\b(senior|lead|principal|staff)\s+([a-z]+\s+)*engineer\b',
            r'\b(technical|engineering|technology)\s+director\b',
            r'\b(engineering|development|technical)\s+manager\b',
            r'\b(senior|lead|principal)\s+architect\b'
        ]

        for pattern in role_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                role = match.group(0).title()
                # Categorize based on keywords
                category = self._categorize_role(role)
                if role.lower() not in [r['role'].lower() for r in found_roles]:
                    found_roles.append({
                        'role': role,
                        'category': category,
                        'match_type': 'pattern'
                    })

        return found_roles

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
            # Add the full role
            keywords.append(role)
            
            # Add variations
            words = role.split()
            if len(words) > 1:
                # Add without seniority level
                if words[0].lower() in ['senior', 'lead', 'principal', 'staff']:
                    keywords.append(' '.join(words[1:]))
                
                # Add core role
                if 'engineer' in role.lower():
                    keywords.append('Software Engineer')
                elif 'manager' in role.lower():
                    keywords.append('Engineering Manager')

        return list(set(keywords))
