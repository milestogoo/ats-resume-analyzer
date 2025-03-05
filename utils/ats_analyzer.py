import re

def analyze_resume(text):
    """
    Analyze resume content for ATS compliance
    """
    # Initialize scores
    format_score = analyze_format(text)
    content_score = analyze_content(text)
    keyword_score = analyze_keywords(text)

    # Calculate overall score
    overall_score = (format_score + content_score + keyword_score) / 3

    # Generate section scores
    section_scores = {
        "Format": format_score,
        "Content": content_score,
        "Keywords": keyword_score
    }

    # Format analysis
    format_analysis = check_format(text)

    # Content analysis
    content_analysis = {
        "Contact Information": check_contact_info(text),
        "Experience": check_experience(text),
        "Education": check_education(text),
        "Skills": check_skills(text)
    }

    # Generate recommendations
    recommendations = generate_recommendations(text, format_analysis, content_analysis)

    # Generate HR snapshot
    hr_snapshot = generate_hr_snapshot(text)

    return {
        "overall_score": round(overall_score, 1),
        "section_scores": section_scores,
        "format_analysis": format_analysis,
        "content_analysis": content_analysis,
        "recommendations": recommendations,
        "hr_snapshot": hr_snapshot
    }

def analyze_format(text):
    """Calculate format compliance score"""
    score = 100
    
    # Check for common format issues
    if len(text.split('\n')) < 10:
        score -= 20
    if len(text) < 200:
        score -= 20
    if re.search(r'[^\x00-\x7F]+', text):  # Check for non-ASCII characters
        score -= 10
        
    return max(0, score)

def analyze_content(text):
    """Calculate content quality score"""
    score = 100
    
    # Basic content checks
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        score -= 20
    if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
        score -= 15
    if not re.search(r'education|experience|skills', text.lower()):
        score -= 25
        
    return max(0, score)

def analyze_keywords(text):
    """Calculate keyword optimization score"""
    keywords = ['experience', 'project', 'skill', 'education', 'achievement', 'responsibility']
    score = 100
    
    text_lower = text.lower()
    for keyword in keywords:
        if keyword not in text_lower:
            score -= 15
            
    return max(0, score)

def check_format(text):
    """Check formatting issues"""
    issues = []
    
    if len(text.split('\n')) < 10:
        issues.append("Resume seems too short or poorly structured")
    if re.search(r'[^\x00-\x7F]+', text):
        issues.append("Contains special characters that may not be ATS-friendly")
    if len(text) < 200:
        issues.append("Content length appears insufficient")
        
    return issues if issues else ["Format appears compliant with ATS requirements"]

def check_contact_info(text):
    """Check contact information section"""
    issues = []
    
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        issues.append("Email address not found or in incorrect format")
    if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
        issues.append("Phone number not found or in incorrect format")
        
    return issues if issues else ["Contact information appears complete"]

def check_experience(text):
    """Check experience section"""
    issues = []
    
    if not re.search(r'experience|work|employment', text.lower()):
        issues.append("Experience section not clearly defined")
    if not re.search(r'(19|20)\d{2}', text):
        issues.append("Dates not found in experience section")
        
    return issues if issues else ["Experience section appears well-structured"]

def check_education(text):
    """Check education section"""
    issues = []
    
    if not re.search(r'education|degree|university|college', text.lower()):
        issues.append("Education section not clearly defined")
        
    return issues if issues else ["Education section appears complete"]

def check_skills(text):
    """Check skills section"""
    issues = []
    
    if not re.search(r'skills|expertise|proficiencies', text.lower()):
        issues.append("Skills section not clearly defined")
        
    return issues if issues else ["Skills section appears well-structured"]

def generate_recommendations(text, format_analysis, content_analysis):
    """Generate recommendations based on analysis"""
    recommendations = {
        "Format Improvements": [],
        "Content Enhancements": [],
        "Keyword Optimization": []
    }
    
    # Format recommendations
    if len(text.split('\n')) < 10:
        recommendations["Format Improvements"].append("Improve resume structure with clear section headings")
    if re.search(r'[^\x00-\x7F]+', text):
        recommendations["Format Improvements"].append("Remove special characters and use standard fonts")
        
    # Content recommendations
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        recommendations["Content Enhancements"].append("Add a professional email address")
    if not re.search(r'experience|work|employment', text.lower()):
        recommendations["Content Enhancements"].append("Clearly label your work experience section")
        
    # Keyword recommendations
    if not re.search(r'skills|expertise|proficiencies', text.lower()):
        recommendations["Keyword Optimization"].append("Add a dedicated skills section with relevant keywords")
    
    return recommendations

def generate_hr_snapshot(text):
    """Generate a quick snapshot of what HR will look for"""
    snapshot = {
        "Quick Stats": {
            "Experience Length": estimate_experience_years(text),
            "Education Level": identify_education_level(text),
            "Key Skills Count": count_key_skills(text),
            "Leadership Indicators": check_leadership_indicators(text)
        },
        "Initial Impressions": [],
        "Potential Red Flags": []
    }

    # Check for essential components
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        snapshot["Potential Red Flags"].append("Missing contact information")

    # Check for clear section headers
    if not all(re.search(term, text.lower()) for term in ['experience', 'education', 'skills']):
        snapshot["Potential Red Flags"].append("Missing standard resume sections")

    # Check for positive indicators
    if re.search(r'\b(achieved|improved|increased|led|managed|developed)\b', text.lower()):
        snapshot["Initial Impressions"].append("Contains strong action verbs")

    if re.search(r'\b\d+%|\d+\s*(million|thousand|k)\b', text.lower()):
        snapshot["Initial Impressions"].append("Includes quantifiable achievements")

    return snapshot

def estimate_experience_years(text):
    """Estimate years of experience from resume text"""
    # Look for year patterns in experience section
    years_pattern = r'(19|20)\d{2}'
    years = re.findall(years_pattern, text)

    if len(years) >= 2:
        years = [int(y) for y in years]
        return f"~{max(years) - min(years)} years"
    return "Unable to determine"

def identify_education_level(text):
    """Identify highest education level"""
    education_levels = {
        r'\bph\.?d\.?\b|\bdoctorate\b': 'Doctorate',
        r"\bmaster'?s?\b|\bm\.?b\.?a\.?\b|\bm\.?s\.?\b|\bm\.?a\.?\b": "Master's",
        r"\bbachelor'?s?\b|\bb\.?s\.?\b|\bb\.?a\.?\b": "Bachelor's",
        r"\bassociate'?s?\b|\ba\.?a\.?\b": "Associate's"
    }

    for pattern, level in education_levels.items():
        if re.search(pattern, text.lower()):
            return level
    return "Not specified"

def count_key_skills(text):
    """Count number of distinct key skills"""
    # Common technical and soft skills to look for
    skill_patterns = [
        r'\b(python|java|javascript|sql|aws|azure)\b',
        r'\b(leadership|management|communication|analysis|planning)\b',
        r'\b(project management|agile|scrum|waterfall)\b'
    ]

    unique_skills = set()
    for pattern in skill_patterns:
        skills = re.findall(pattern, text.lower())
        unique_skills.update(skills)

    return len(unique_skills)

def check_leadership_indicators(text):
    """Check for leadership experience indicators"""
    leadership_terms = [
        r'\b(managed|led|supervised|directed|coordinated)\b',
        r'\b(team|group|department|division)\b',
        r'\b(leadership|manager|director|supervisor|head)\b'
    ]

    indicators = []
    for term in leadership_terms:
        if re.search(term, text.lower()):
            indicators.append(True)

    return "Strong" if len(indicators) >= 2 else "Limited" if indicators else "None"