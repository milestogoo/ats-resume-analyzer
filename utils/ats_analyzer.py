import re

def analyze_resume(text):
    """
    Analyze resume content for ATS compliance with detailed recommendations
    """
    # Initialize scores and analysis
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

    # Detailed analysis for each section
    format_analysis = check_format(text)
    content_analysis = {
        "Contact Information": check_contact_info(text),
        "Professional Summary": check_summary(text),
        "Work Experience": check_experience(text),
        "Education": check_education(text),
        "Skills": check_skills(text),
        "Achievements": check_achievements(text)
    }

    # Generate comprehensive recommendations
    recommendations = generate_detailed_recommendations(text, format_analysis, content_analysis)

    return {
        "overall_score": round(overall_score, 1),
        "section_scores": section_scores,
        "format_analysis": format_analysis,
        "content_analysis": content_analysis,
        "recommendations": recommendations
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
    """Enhanced format checking"""
    issues = []

    # Length checks
    if len(text.split('\n')) < 10:
        issues.append("Resume length is insufficient for ATS scanning")

    # Special character checks
    if re.search(r'[^\x00-\x7F]+', text):
        issues.append("Contains special characters that may cause ATS parsing errors")

    # Bullet point consistency
    bullet_points = re.findall(r'[•·○●▪︎]', text)
    if len(set(bullet_points)) > 1:
        issues.append("Inconsistent bullet point formats detected")

    # Section headings
    if not re.search(r'^[A-Z\s]{2,}(?:\r?\n|\r|$)', text, re.MULTILINE):
        issues.append("Section headings may not be clearly formatted")

    return issues if issues else ["Format appears compliant with ATS requirements"]

def check_contact_info(text):
    """Check contact information section"""
    issues = []
    
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        issues.append("Email address not found or in incorrect format")
    if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
        issues.append("Phone number not found or in incorrect format")
        
    return issues if issues else ["Contact information appears complete"]

def check_summary(text):
    """Check professional summary section"""
    issues = []
    summary_patterns = [
        r'summary|profile|objective|about',
        r'years? of experience',
        r'professional|expert|specialist'
    ]

    if not any(re.search(pattern, text.lower()) for pattern in summary_patterns):
        issues.append("Professional summary section not found or unclear")
    if len(re.findall(r'[.!?]', text.split('\n')[0:5])) < 2:
        issues.append("Summary appears too brief or incomplete")

    return issues if issues else ["Professional summary appears well-written"]

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

def check_achievements(text):
    """Check achievements and impact statements"""
    issues = []

    # Check for quantifiable achievements
    if not re.search(r'\d+%|\$\d+|\d+ [a-zA-Z]+', text):
        issues.append("No quantifiable achievements found")

    # Check for action verbs
    action_verbs = ['achieved', 'led', 'developed', 'managed', 'created', 'implemented']
    if not any(verb in text.lower() for verb in action_verbs):
        issues.append("Limited use of strong action verbs")

    return issues if issues else ["Achievements section includes quantifiable results"]

def generate_detailed_recommendations(text, format_analysis, content_analysis):
    """Generate detailed, actionable recommendations"""
    recommendations = {
        "High Priority Fixes": [],
        "Format Improvements": [],
        "Content Enhancements": [],
        "Keyword Optimization": [],
        "Section-Specific Recommendations": []
    }

    # High Priority Fixes
    if len(text.split('\n')) < 10:
        recommendations["High Priority Fixes"].append(
            "⚠️ Resume is too short. Aim for 2-3 pages for experienced professionals, 1-2 pages for entry-level"
        )

    # Format Improvements
    if re.search(r'[^\x00-\x7F]+', text):
        recommendations["Format Improvements"].extend([
            "Replace special characters with standard ASCII alternatives",
            "Use standard bullet points (•) instead of fancy symbols",
            "Ensure consistent spacing between sections (double space recommended)"
        ])

    # Content Enhancements
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        recommendations["Content Enhancements"].extend([
            "Add a professional email address at the top of the resume",
            "Include LinkedIn profile URL using standard format",
            "Add current location (city, state) to contact section"
        ])

    # Keyword Optimization
    common_skills = ['leadership', 'project management', 'communication', 'analytics']
    missing_skills = [skill for skill in common_skills if skill not in text.lower()]
    if missing_skills:
        recommendations["Keyword Optimization"].extend([
            f"Add relevant skills: {', '.join(missing_skills)}",
            "Include both full terms and acronyms (e.g., 'Project Management (PM)')",
            "Incorporate industry-specific keywords from job descriptions"
        ])

    # Section-Specific Recommendations
    if not re.search(r'\d+%|\$\d+|\d+ [a-zA-Z]+', text):
        recommendations["Section-Specific Recommendations"].extend([
            "Quantify achievements (e.g., 'Increased sales by 25%', 'Managed team of 12')",
            "Use strong action verbs to start bullet points",
            "Include 3-5 bullet points per role, focusing on impacts"
        ])

    return recommendations