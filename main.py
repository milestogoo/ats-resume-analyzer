import streamlit as st
import pandas as pd
from utils.file_parser import parse_resume
from utils.ats_analyzer import analyze_resume
from utils.visualizer import create_score_chart, create_section_breakdown

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

st.title("📄 ATS Resume Analyzer")
st.markdown("""
    Upload your resume to check its ATS compliance and get detailed recommendations.
    Supported formats: PDF, DOC, DOCX
""")

uploaded_file = st.file_uploader("Choose your resume file", type=['pdf', 'doc', 'docx'])

if uploaded_file is not None:
    try:
        # Parse the resume
        resume_text, file_format = parse_resume(uploaded_file)

        # Analyze the content
        analysis_results = analyze_resume(resume_text)

        # Display Results
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Overall ATS Compliance Score")
            create_score_chart(analysis_results['overall_score'])

        with col2:
            st.subheader("Section-wise Breakdown")
            create_section_breakdown(analysis_results['section_scores'])

        # HR Quick View
        st.subheader("💼 HR Quick View")
        hr_snapshot = analysis_results['hr_snapshot']

        # Display Quick Stats in a modern card layout
        st.markdown("""
        <div class="hr-stats-container">
            <h3>Quick Stats</h3>
        </div>
        """, unsafe_allow_html=True)

        quick_stats = hr_snapshot['Quick Stats']

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

        tabs = st.tabs(["Format Analysis", "Content Analysis", "Recommendations"])

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

    except Exception as e:
        st.error(f"An error occurred while processing your file: {str(e)}")

else:
    st.info("Please upload a resume to begin the analysis.")