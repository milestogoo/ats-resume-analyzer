import streamlit as st
import pandas as pd
from utils.file_parser import parse_resume
from utils.ats_analyzer import analyze_resume
from utils.visualizer import create_score_chart, create_section_breakdown
from utils.role_extractor import RoleExtractor
from utils.job_crawler import JobCrawler
from datetime import datetime
import base64

# Initialize components
role_extractor = RoleExtractor()
job_crawler = JobCrawler()

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'is_first_upload' not in st.session_state:
    st.session_state.is_first_upload = True
if 'extracted_roles' not in st.session_state:
    st.session_state.extracted_roles = []
if 'job_recommendations' not in st.session_state:
    st.session_state.job_recommendations = {}
if 'job_filter_period' not in st.session_state:
    st.session_state.job_filter_period = 'all'
if 'selected_countries' not in st.session_state:
    st.session_state.selected_countries = ['India']
if 'selected_roles' not in st.session_state:
    st.session_state.selected_roles = []
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = ['Indeed', 'Naukri', 'LinkedIn']


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Job Search Filters")

    # Date filter
    st.markdown("#### 📅 Posted Date")
    filter_options = [
        ("All Time", "all"),
        ("Today", "today"),
        ("Last 3 Days", "3days"),
        ("Last Week", "7days"),
        ("Last 3 Weeks", "21days")
    ]

    selected_period = st.radio(
        "Select time period",
        options=[opt[0] for opt in filter_options],
        key="date_filter",
        label_visibility="collapsed"
    )

    # Update job filter period based on selection
    st.session_state.job_filter_period = dict(filter_options)[selected_period]

    # Country filter
    st.markdown("#### 🌍 Location")
    countries = ['India', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Singapore', 'Germany']
    st.session_state.selected_countries = st.multiselect(
        "Select countries",
        options=countries,
        default=['India'],
        key="country_filter",
        label_visibility="collapsed"
    )

    # Source filter
    st.markdown("#### 🔗 Job Sources")
    sources = ['Indeed', 'Naukri', 'LinkedIn']

    st.session_state.selected_sources = st.multiselect(
        "Select job sources",
        options=sources,
        default=sources,
        key="source_filter",
        label_visibility="collapsed"
    )

    # Role filter (dynamically populated when resume is uploaded)
    if st.session_state.extracted_roles:
        st.markdown("#### 👔 Roles")
        available_roles = set(role['category'] for role in st.session_state.extracted_roles)
        st.session_state.selected_roles = st.multiselect(
            "Select roles",
            options=list(available_roles),
            default=list(available_roles),
            key="role_filter",
            label_visibility="collapsed"
        )

# Main content area
st.markdown("""
    <div class="logo-container">
        <svg width="250" height="100" viewBox="0 0 250 100">
            <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#1A237E"/>
                    <stop offset="100%" style="stop-color:#3F51B5"/>
                </linearGradient>
            </defs>
            <rect width="250" height="100" rx="15" fill="url(#logoGradient)"/>
            <text x="50%" y="40%" dominant-baseline="middle" text-anchor="middle" 
                  fill="#FFD700" style="font-size: 45px; font-weight: bold;">
                ATS
            </text>
            <text x="50%" y="70%" dominant-baseline="middle" text-anchor="middle" 
                  fill="#FFFFFF" style="font-size: 20px;">
                Resume Analyzer
            </text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

# Upload section
st.markdown("### 📤 Upload Your Resume")
uploaded_file = st.file_uploader("", type=['pdf', 'doc', 'docx'])

if uploaded_file is not None:
    try:
        with st.spinner('Analyzing your resume...'):
            # Parse and analyze the resume
            resume_text, file_format = parse_resume(uploaded_file)
            analysis_results = analyze_resume(resume_text)

            # Extract roles and search for jobs
            extracted_roles = role_extractor.extract_roles(resume_text)
            search_keywords = role_extractor.get_search_keywords(extracted_roles)

            # Store results
            st.session_state.analysis_results[uploaded_file.name] = analysis_results
            st.session_state.upload_history.append({
                "filename": uploaded_file.name,
                "timestamp": datetime.now(),
                "score": analysis_results['overall_score']
            })
            st.session_state.upload_history = st.session_state.upload_history[-5:]
            st.session_state.extracted_roles = extracted_roles

        # Show recent uploads in collapsible section
        if st.session_state.upload_history:
            with st.expander("📊 Recent Uploads", expanded=st.session_state.is_first_upload):
                history_data = [{
                    "filename": entry["filename"],
                    "timestamp": entry["timestamp"],
                    "score": entry["score"],
                    "download": f"📥 {entry['filename']}"
                } for entry in st.session_state.upload_history]

                history_df = pd.DataFrame(history_data)
                st.dataframe(
                    history_df,
                    column_config={
                        "filename": "File Name",
                        "timestamp": st.column_config.DatetimeColumn(
                            "Upload Time",
                            format="DD/MM/YY HH:mm"
                        ),
                        "score": st.column_config.ProgressColumn(
                            "ATS Score",
                            min_value=0,
                            max_value=100,
                            format="%d%%"
                        ),
                        "download": st.column_config.LinkColumn(
                            "Download Report",
                            help="Click to download the analysis report"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )

            if st.session_state.is_first_upload:
                st.session_state.is_first_upload = False

            # Add HR Snapshot Section
            st.markdown("""
                <div class='section-header'>
                    <h3>👔 HR Quick View</h3>
                </div>
            """, unsafe_allow_html=True)

            # Get HR snapshot data
            hr_snapshot = analysis_results['hr_snapshot']
            quick_stats = hr_snapshot['Quick Stats']

            # Create three columns for key metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                    <div class='metric-card'>
                        <div class='metric-icon'>⏳</div>
                        <div class='metric-content'>
                            <h4>Experience</h4>
                            <p class='metric-value'>{}</p>
                        </div>
                    </div>
                """.format(quick_stats['Experience']), unsafe_allow_html=True)

            with col2:
                edu_details = quick_stats['Education']
                if isinstance(edu_details, dict):
                    edu_text = f"{edu_details['level']} in {edu_details['major']}"
                else:
                    edu_text = edu_details
                st.markdown("""
                    <div class='metric-card'>
                        <div class='metric-icon'>🎓</div>
                        <div class='metric-content'>
                            <h4>Education</h4>
                            <p class='metric-value'>{}</p>
                        </div>
                    </div>
                """.format(edu_text), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                    <div class='metric-card'>
                        <div class='metric-icon'>👥</div>
                        <div class='metric-content'>
                            <h4>Leadership Level</h4>
                            <p class='metric-value'>{}</p>
                        </div>
                    </div>
                """.format(quick_stats['Leadership Indicators']), unsafe_allow_html=True)

            # Skills and competencies
            st.markdown("### 🎯 Core Competencies")
            skills = quick_stats['Skills']
            skill_cols = st.columns(3)

            with skill_cols[0]:
                st.markdown("**💻 Technical Skills**")
                if skills['Technical']:
                    st.markdown("\n".join([f"- {skill.title()}" for skill in skills['Technical']]))
                else:
                    st.info("No technical skills identified")

            with skill_cols[1]:
                st.markdown("**🤝 Soft Skills**")
                if skills['Soft Skills']:
                    st.markdown("\n".join([f"- {skill.title()}" for skill in skills['Soft Skills']]))
                else:
                    st.info("No soft skills identified")

            with skill_cols[2]:
                st.markdown("**🔧 Tools & Platforms**")
                if skills['Tools']:
                    st.markdown("\n".join([f"- {tool.title()}" for tool in skills['Tools']]))
                else:
                    st.info("No tools/platforms identified")

            # Key Highlights
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### ✨ Key Highlights")
                if hr_snapshot['Initial Impressions']:
                    for impression in hr_snapshot['Initial Impressions']:
                        st.markdown(f"✓ {impression}")
                else:
                    st.info("No key highlights identified")

            with col2:
                st.markdown("### ⚠️ Areas for Review")
                if hr_snapshot['Potential Red Flags']:
                    for flag in hr_snapshot['Potential Red Flags']:
                        st.markdown(f"• {flag}")
                else:
                    st.success("No significant concerns identified")


            # Add Job Recommendations
            if extracted_roles:
                st.markdown("""
                    <div class='section-header'>
                        <h3>💼 Job Recommendations</h3>
                    </div>
                """, unsafe_allow_html=True)

                with st.spinner("Searching for relevant jobs..."):
                    jobs = job_crawler.search_jobs(
                        search_keywords,
                        location=", ".join(st.session_state.selected_countries)
                    )
                    filtered_jobs = job_crawler.filter_jobs_by_date(jobs, st.session_state.job_filter_period)

                    # Filter by selected sources
                    filtered_jobs = [
                        job for job in filtered_jobs
                        if job['source'] in st.session_state.selected_sources
                    ]

                    if st.session_state.selected_roles:
                        filtered_jobs = [
                            job for job in filtered_jobs
                            if any(role.lower() in job['title'].lower()
                                      for role in st.session_state.selected_roles)
                        ]

                    categorized_jobs = job_crawler.format_jobs_for_display(filtered_jobs)

                    # Create tabs for job categories
                    job_tabs = st.tabs([cat.title() for cat in categorized_jobs.keys()])

                    for tab, (category, jobs) in zip(job_tabs, categorized_jobs.items()):
                        with tab:
                            if jobs:
                                for job in jobs:
                                    st.markdown(f"""
                                    <div class='job-card'>
                                        <h4>{job['title']}</h4>
                                        <p class='job-meta'>
                                            {job['company']} • {job['location']}
                                            <span class='job-source'>{job['source']}</span>
                                            <span class='job-date'>Posted: {job['posted_date']}</span>
                                        </p>
                                        <div class='job-divider'></div>
                                        <p class='job-description'>{job['description']}</p>
                                        <a href='{job['url']}' target='_blank' class='job-link'>
                                            View Details →
                                        </a>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(f"No {category} jobs found")

            # Results section
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Overall ATS Compliance")
                create_score_chart(analysis_results['overall_score'])

            with col2:
                st.markdown("### Detailed Breakdown")
                create_section_breakdown(analysis_results['section_scores'])

    except Exception as e:
        st.error(f"An error occurred while processing your file: {str(e)}")

# Handle downloads through markdown
if st.session_state.upload_history:
    for entry in st.session_state.upload_history:
        analysis_data = str(st.session_state.analysis_results.get(entry['filename'], {}))
        b64_data = base64.b64encode(analysis_data.encode()).decode()
        st.markdown(f"""
            <div style="display: none;">
                <a id="download_{entry['filename']}" 
                   href="data:text/plain;base64,{b64_data}" 
                   download="{entry['filename']}_analysis.txt">
                </a>
            </div>""",
            unsafe_allow_html=True
        )