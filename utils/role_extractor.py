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
        Extract job roles from resume text with experience levels
        Returns list of roles with their categories and experience levels
        """
        found_roles = []
        text_lower = text.lower()

        # Look for exact matches first
        for category, roles in self.common_roles.items():
            for role in roles:
                role_lower = role.lower()
                if role_lower in text_lower:
                    # Get experience context
                    exp_level = self._get_experience_level(text_lower, role_lower)
                    found_roles.append({
                        'role': role,
                        'category': category,
                        'match_type': 'exact',
                        'experience_level': exp_level
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
                category = self._categorize_role(role)
                exp_level = self._get_experience_level(text_lower, role.lower())
                if role.lower() not in [r['role'].lower() for r in found_roles]:
                    found_roles.append({
                        'role': role,
                        'category': category,
                        'match_type': 'pattern',
                        'experience_level': exp_level
                    })

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