import re
from utils.ml_scorer import MLScorer

# Initialize ML scorer
ml_scorer = MLScorer()

def analyze_resume(text):
    """
    Analyze resume content for ATS compliance
    """
    # Initialize scores
    format_score = analyze_format(text)
    content_score = analyze_content(text)
    keyword_score = analyze_keywords(text)

    # Get ML-based score
    ml_score = ml_scorer.predict_score(text)

    # Calculate overall score (25% each for format, content, keywords, and ML score)
    overall_score = (format_score + content_score + keyword_score + ml_score) / 4

    # Generate section scores
    section_scores = {
        "Format": format_score,
        "Content": content_score,
        "Keywords": keyword_score,
        "ML Score": ml_score
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
    """Generate detailed recommendations based on analysis"""
    recommendations = {
        "High Priority": [],
        "Format Improvements": [],
        "Content Enhancements": [],
        "Keyword Optimization": []
    }

    # High priority recommendations
    if len(text.split('\n')) < 10:
        recommendations["High Priority"].append({
            "issue": "Resume structure needs improvement",
            "action": "Add clear section headings (Experience, Education, Skills)",
            "impact": "Improves ATS parsing accuracy by 40%"
        })
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        recommendations["High Priority"].append({
            "issue": "Missing contact information",
            "action": "Add professional email address in header section",
            "impact": "Essential for recruiter contact"
        })

    # Format recommendations
    if re.search(r'[^\x00-\x7F]+', text):
        recommendations["Format Improvements"].append({
            "issue": "Special characters detected",
            "action": "Replace special characters with standard ASCII alternatives",
            "impact": "Ensures proper ATS parsing"
        })
    if len(text) < 500:
        recommendations["Format Improvements"].append({
            "issue": "Resume content length is insufficient",
            "action": "Expand on experience and achievements (aim for 500-1000 words)",
            "impact": "Better keyword coverage and readability"
        })

    # Content recommendations
    if not re.search(r'experience|work|employment', text.lower()):
        recommendations["Content Enhancements"].append({
            "issue": "Work experience section not clearly defined",
            "action": "Add clear 'Professional Experience' section with bullet points",
            "impact": "Improves experience visibility to ATS"
        })
    if not re.search(r'\b(achieved|improved|increased|led|managed|developed)\b', text.lower()):
        recommendations["Content Enhancements"].append({
            "issue": "Limited action verbs",
            "action": "Include strong action verbs to describe achievements",
            "impact": "Demonstrates impact and leadership"
        })

    # Keyword optimization
    if not re.search(r'skills|expertise|proficiencies', text.lower()):
        recommendations["Keyword Optimization"].append({
            "issue": "Skills section not optimized",
            "action": "Add dedicated skills section with industry-specific keywords",
            "impact": "Increases ATS matching score"
        })
    if not re.search(r'\b\d+%|\d+\s*(million|thousand|k)\b', text.lower()):
        recommendations["Keyword Optimization"].append({
            "issue": "Missing quantifiable achievements",
            "action": "Add metrics and numbers to demonstrate impact",
            "impact": "Makes achievements more concrete"
        })

    return recommendations

def generate_hr_snapshot(text):
    """Generate a quick snapshot of what HR will look for"""
    snapshot = {
        "Quick Stats": {
            "Experience": estimate_experience_years(text),
            "Education": identify_education_level(text),
            "Skills": identify_key_skills(text),
            "Leadership Indicators": check_leadership_indicators(text)
        },
        "Initial Impressions": [],
        "Potential Red Flags": []
    }

    # Check for essential components
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        snapshot["Potential Red Flags"].append("Missing contact information")

    # Check for missing sections
    missing_sections = check_missing_sections(text)
    if missing_sections:
        for section in missing_sections:
            snapshot["Potential Red Flags"].append(f"Missing {section} section")

    # Check for positive indicators
    if re.search(r'\b(achieved|improved|increased|led|managed|developed)\b', text.lower()):
        snapshot["Initial Impressions"].append("Contains strong action verbs")

    if re.search(r'\b\d+%|\d+\s*(million|thousand|k)\b', text.lower()):
        snapshot["Initial Impressions"].append("Includes quantifiable achievements")

    return snapshot

def estimate_experience_years(text):
    """Estimate years of experience from resume text"""
    # First look for experience section
    exp_section = re.search(r'(?i)experience.*?(?=education|skills|$)', text, re.DOTALL)
    if exp_section:
        text_to_search = exp_section.group(0)
    else:
        text_to_search = text

    # Look for year patterns
    years_pattern = r'(19|20)\d{2}'
    years = re.findall(years_pattern, text_to_search)

    if len(years) >= 2:
        years = [int(y) for y in years]
        latest_year = max(years)
        earliest_year = min(years)
        # If latest year is in future, use current year
        if latest_year > 2025:
            latest_year = 2025
        return f"{latest_year - earliest_year} years ({earliest_year} - {latest_year})"
    return "Experience timeline not clear"

def identify_education_level(text):
    """Identify highest education level and details"""
    education_section = re.search(r'(?i)education.*?(?=experience|skills|$)', text, re.DOTALL)
    if not education_section:
        return "Education details not found"

    edu_text = education_section.group(0)
    education_details = {
        'level': 'Not specified',
        'major': 'Not specified',
        'institution': 'Not specified'
    }

    # Check education level
    levels = {
        r'\bph\.?d\.?\b|\bdoctorate\b': 'Doctorate',
        r"\bmaster'?s?\b|\bm\.?b\.?a\.?\b|\bm\.?s\.?\b|\bm\.?a\.?\b": "Master's",
        r"\bbachelor'?s?\b|\bb\.?s\.?\b|\bb\.?a\.?\b": "Bachelor's",
        r"\bassociate'?s?\b|\ba\.?a\.?\b": "Associate's"
    }

    for pattern, level in levels.items():
        if re.search(pattern, edu_text.lower()):
            education_details['level'] = level
            break

    # Try to identify major
    major_patterns = [
        r'(?i)in\s+([\w\s]+?)(?=from|at|,|\d|$)',
        r'(?i)of\s+([\w\s]+?)(?=from|at|,|\d|$)',
        r'(?i)(computer science|engineering|business|psychology|mathematics|physics|chemistry|biology|economics|finance|marketing|management|accounting|communications|english|history|philosophy|political science|sociology)([\s,]|$)'
    ]

    for pattern in major_patterns:
        major_match = re.search(pattern, edu_text)
        if major_match:
            education_details['major'] = major_match.group(1).strip().title()
            break

    # Try to identify institution
    inst_match = re.search(r'(?i)(?:at|from)\s+([\w\s&]+?)(?=\sin|,|\d|$)', edu_text)
    if inst_match:
        education_details['institution'] = inst_match.group(1).strip().title()

    return education_details

def identify_key_skills(text):
    """Identify specific key skills from the resume"""
    skills_section = re.search(r'(?i)skills.*?(?=experience|education|$)', text, re.DOTALL)
    if skills_section:
        text_to_search = skills_section.group(0)
    else:
        text_to_search = text

    skill_categories = {
        'Technical': [
            r'\b(python|java|javascript|typescript|react|angular|vue|node\.js|sql|aws|azure|docker|kubernetes|git)\b',
            r'\b(html5|css3|rest api|graphql|mongodb|postgresql|mysql|redis|elasticsearch)\b',
            r'\b(machine learning|artificial intelligence|data science|cloud computing|devops|ci/cd)\b'
        ],
        'Soft Skills': [
            r'\b(leadership|management|communication|teamwork|problem.solving|analytical)\b',
            r'\b(project management|time management|critical thinking|decision making|negotiation)\b'
        ],
        'Tools': [
            r'\b(jira|confluence|slack|microsoft office|excel|powerpoint|photoshop|figma|sketch)\b',
            r'\b(visual studio|intellij|eclipse|postman|jenkins|terraform|ansible)\b'
        ]
    }

    identified_skills = {category: set() for category in skill_categories}

    for category, patterns in skill_categories.items():
        for pattern in patterns:
            skills = re.findall(pattern, text_to_search.lower())
            identified_skills[category].update(skills)

    # Convert sets to sorted lists
    return {category: sorted(list(skills)) for category, skills in identified_skills.items()}

def check_missing_sections(text):
    """Check for missing standard resume sections"""
    standard_sections = {
        'Contact Information': r'\b(?:phone|email|address|linkedin)\b',
        'Summary/Objective': r'\b(?:summary|objective|profile|about)\b',
        'Experience': r'\b(?:experience|work|employment|career)\b',
        'Education': r'\b(?:education|degree|university|college)\b',
        'Skills': r'\b(?:skills|expertise|competencies|proficiencies)\b',
        'Projects': r'\b(?:projects|portfolio|achievements)\b'
    }

    missing_sections = []
    for section, pattern in standard_sections.items():
        if not re.search(pattern, text.lower()):
            missing_sections.append(section)

    return missing_sections

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