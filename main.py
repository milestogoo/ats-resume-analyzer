import streamlit as st
import pandas as pd
from utils.file_parser import parse_resume
from utils.ats_analyzer import analyze_resume
from utils.visualizer import create_score_chart, create_section_breakdown
from utils.linkedin_auth import LinkedInOAuth
from datetime import datetime
import base64

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'linkedin_oauth_state' not in st.session_state:
    st.session_state.linkedin_oauth_state = None

local_css("assets/style.css")

# Custom header with logo
st.markdown("""
    <div class="header-container">
        <div class="logo-title">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <rect width="40" height="40" rx="8" fill="#2196F3"/>
                <path d="M12 20L18 26L28 14" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h1>ATS Resume Analyzer</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display upload history if exists
if st.session_state.upload_history:
    st.markdown("#### 📊 Recent Uploads")

    # Create DataFrame with download buttons
    history_data = []
    for entry in st.session_state.upload_history:
        history_data.append({
            "filename": entry["filename"],
            "timestamp": entry["timestamp"],
            "score": entry["score"],
            "download": f"📥 {entry['filename']}"  # We'll handle the button click separately
        })

    history_df = pd.DataFrame(history_data)

    # Display the dataframe
    clicked = st.dataframe(
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

    # Handle downloads through markdown
    for entry in st.session_state.upload_history:
        analysis_data = str(st.session_state.analysis_results.get(entry['filename'], {}))
        b64_data = base64.b64encode(analysis_data.encode()).decode()
        st.markdown(
            f"""<div style="display: none;">
                <a id="download_{entry['filename']}" 
                   href="data:text/plain;base64,{b64_data}" 
                   download="{entry['filename']}_analysis.txt">
                </a>
            </div>""",
            unsafe_allow_html=True
        )

# File Upload Section with LinkedIn Import
st.markdown("""
    <div class="app-description">
        Upload your resume to check its ATS compliance and get detailed recommendations.
        Supported formats: PDF, DOC, DOCX
    </div>
    """, unsafe_allow_html=True)

# Add LinkedIn import button
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("Choose your resume file", type=['pdf', 'doc', 'docx'])

with col2:
    linkedin_auth = LinkedInOAuth()
    if st.button("📎 Import from LinkedIn", type="secondary"):
        auth_url, state = linkedin_auth.get_auth_url()
        st.session_state.linkedin_oauth_state = state
        st.markdown(f'<a href="{auth_url}" target="_blank">Click here to authorize LinkedIn</a>', unsafe_allow_html=True)
        st.info("After authorizing, you'll be redirected back to this page.")

# Handle LinkedIn callback
if 'code' in st.query_params:
    try:
        code = st.query_params['code']
        full_redirect_uri = f"{linkedin_auth.redirect_uri}?code={code}"
        token = linkedin_auth.fetch_token(full_redirect_uri)
        profile_data = linkedin_auth.get_profile_data(token)
        st.success(f"Successfully imported profile for {profile_data['firstName']} {profile_data['lastName']}")
        # Process LinkedIn data here (Further implementation needed)
    except Exception as e:
        st.error(f"Error importing LinkedIn profile: {str(e)}")


if uploaded_file is not None:
    try:
        # Parse the resume
        resume_text, file_format = parse_resume(uploaded_file)

        # Analyze the content
        analysis_results = analyze_resume(resume_text)

        # Store analysis results in session state
        st.session_state.analysis_results[uploaded_file.name] = analysis_results

        # Add to upload history
        st.session_state.upload_history.append({
            "filename": uploaded_file.name,
            "timestamp": datetime.now(),
            "score": analysis_results['overall_score']
        })
        # Keep only last 5 entries
        st.session_state.upload_history = st.session_state.upload_history[-5:]

        # Display Results in a clean layout
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Overall ATS Compliance Score")
            create_score_chart(analysis_results['overall_score'])

        with col2:
            st.subheader("Section-wise Breakdown")
            create_section_breakdown(analysis_results['section_scores'])

        st.markdown('</div>', unsafe_allow_html=True)

        # HR Quick View
        st.subheader("💼 HR Quick View")
        hr_snapshot = analysis_results['hr_snapshot']
        quick_stats = hr_snapshot['Quick Stats']

        # Display Quick Stats in a modern card layout
        st.markdown("""
        <div class="hr-stats-container">
            <h3>Quick Stats</h3>
        </div>
        """, unsafe_allow_html=True)


        # Experience and Leadership
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Experience", quick_stats['Experience'])
        with col2:
            st.metric("Leadership", quick_stats['Leadership Indicators'])

        # Education Details
        st.markdown("#### 🎓 Education")
        edu_details = quick_stats['Education']
        if isinstance(edu_details, dict):
            edu_cols = st.columns(3)
            with edu_cols[0]:
                st.metric("Level", edu_details['level'])
            with edu_cols[1]:
                st.metric("Major", edu_details['major'])
            with edu_cols[2]:
                st.metric("Institution", edu_details['institution'])
        else:
            st.info(edu_details)

        # Skills Breakdown
        st.markdown("#### 🛠️ Skills Identified")
        skills = quick_stats['Skills']
        skill_cols = st.columns(3)

        with skill_cols[0]:
            st.markdown("**Technical Skills**")
            if skills['Technical']:
                for skill in skills['Technical']:
                    st.markdown(f"- {skill.title()}")
            else:
                st.info("No technical skills identified")

        with skill_cols[1]:
            st.markdown("**Soft Skills**")
            if skills['Soft Skills']:
                for skill in skills['Soft Skills']:
                    st.markdown(f"- {skill.title()}")
            else:
                st.info("No soft skills identified")

        with skill_cols[2]:
            st.markdown("**Tools & Platforms**")
            if skills['Tools']:
                for tool in skills['Tools']:
                    st.markdown(f"- {tool.title()}")
            else:
                st.info("No tools/platforms identified")

        # Display Initial Impressions and Red Flags
        st.markdown("#### 📋 Overview")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**✅ Initial Impressions**")
            for impression in hr_snapshot['Initial Impressions']:
                st.markdown(f"- {impression}")

        with col2:
            st.markdown("**⚠️ Potential Red Flags**")
            for flag in hr_snapshot['Potential Red Flags']:
                st.markdown(f"- {flag}")

        # Detailed Analysis
        st.subheader("Detailed Analysis")

        tabs = st.tabs(["Format Analysis", "Content Analysis", "Recommendations", "Raw Data"])

        with tabs[0]:
            st.markdown("### Format Compliance")
            for item in analysis_results['format_analysis']:
                st.markdown(f"- {item}")

        with tabs[1]:
            st.markdown("### Content Analysis")
            for section, details in analysis_results['content_analysis'].items():
                st.markdown(f"**{section}**")
                for detail in details:
                    st.markdown(f"- {detail}")

        with tabs[2]:
            st.markdown("### Recommendations")
            for category, recommendations in analysis_results['recommendations'].items():
                st.markdown(f"**{category}**")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

        with tabs[3]:
            st.markdown("### 📝 Raw Analysis Data")
            st.json(analysis_results)

    except Exception as e:
        st.error(f"An error occurred while processing your file: {str(e)}")