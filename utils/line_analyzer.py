import re
from typing import List, Dict, Tuple

class LineAnalyzer:
    def __init__(self):
        self.action_verbs = {
            'achieved', 'improved', 'led', 'managed', 'developed', 'created',
            'implemented', 'increased', 'decreased', 'coordinated', 'supervised',
            'launched', 'designed', 'established', 'transformed', 'optimized'
        }
        
        self.weak_words = {
            'helped', 'worked', 'responsible', 'handled', 'duties', 'various',
            'assisted', 'things', 'stuff', 'did', 'tried', 'attempted'
        }

    def analyze_line(self, line: str) -> Dict:
        """Analyze a single line of resume text"""
        result = {
            'line': line,
            'score': 100,
            'suggestions': [],
            'improvements': [],
            'style': 'good'  # can be 'good', 'warning', 'critical'
        }
        
        # Skip empty lines
        if not line.strip():
            return result
            
        # Check line length
        if len(line) > 100:
            result['score'] -= 10
            result['suggestions'].append("Line is too long - consider breaking into two")
            result['style'] = 'warning'
            
        # Check for weak words
        weak_words_found = [word for word in self.weak_words if word in line.lower()]
        if weak_words_found:
            result['score'] -= 5 * len(weak_words_found)
            result['suggestions'].append(f"Replace weak words: {', '.join(weak_words_found)}")
            result['improvements'].extend([
                f"Replace '{word}' with a stronger action verb" for word in weak_words_found
            ])
            result['style'] = 'warning'
            
        # Check for numbers and metrics
        if not re.search(r'\d+%|\d+', line):
            if re.search(r'increased|decreased|improved|reduced|achieved', line.lower()):
                result['score'] -= 15
                result['suggestions'].append("Add specific metrics/numbers to quantify achievement")
                result['style'] = 'warning'
                
        # Check for action verbs
        if any(verb in line.lower() for verb in self.action_verbs):
            result['score'] += 5
        else:
            first_word = line.strip().split()[0].lower() if line.strip() else ''
            if not first_word.istitle() and not any(c.isdigit() for c in first_word):
                result['score'] -= 10
                result['suggestions'].append("Start with an action verb")
                result['style'] = 'warning'
                
        # Check for special characters
        if re.search(r'[^\x00-\x7F]+', line):
            result['score'] -= 20
            result['suggestions'].append("Remove special characters")
            result['style'] = 'critical'
            
        # Check for proper capitalization
        if not line[0].isupper() and line.strip():
            result['score'] -= 5
            result['suggestions'].append("Start with a capital letter")
            result['style'] = 'warning'
            
        # Normalize score
        result['score'] = max(0, min(100, result['score']))
        
        # Set final style based on score
        if result['score'] < 50:
            result['style'] = 'critical'
        elif result['score'] < 80:
            result['style'] = 'warning'
            
        return result

    def analyze_section(self, section: str, section_name: str) -> List[Dict]:
        """Analyze a section of the resume"""
        lines = section.split('\n')
        results = []
        
        for line in lines:
            line_result = self.analyze_line(line)
            
            # Add section-specific checks
            if section_name.lower() == 'experience':
                if not re.search(r'(19|20)\d{2}', line):
                    line_result['suggestions'].append("Consider adding dates")
                    line_result['score'] -= 5
                    
            elif section_name.lower() == 'education':
                if not re.search(r'degree|diploma|certificate|bachelor|master|phd', line.lower()):
                    line_result['suggestions'].append("Specify degree/qualification")
                    line_result['score'] -= 5
                    
            elif section_name.lower() == 'skills':
                if ',' not in line and len(line.split()) > 4:
                    line_result['suggestions'].append("Use commas to separate skills")
                    line_result['score'] -= 5
                    
            results.append(line_result)
            
        return results

    def get_improvement_suggestions(self, line_result: Dict) -> List[str]:
        """Get specific improvement suggestions for a line"""
        suggestions = []
        
        # Add specific suggestions based on the analysis
        if 'Start with an action verb' in line_result['suggestions']:
            suggestions.append("Try starting with verbs like: Developed, Implemented, Led, Managed")
            
        if 'Add specific metrics/numbers' in line_result['suggestions']:
            suggestions.append("Example: 'Increased sales by 25%' instead of 'Increased sales'")
            
        if 'Line is too long' in line_result['suggestions']:
            suggestions.append("Break into bullet points or shorter, focused statements")
            
        return suggestions or line_result['improvements']
