import streamlit as st
import pandas as pd
from utils.file_parser import parse_resume
from utils.ats_analyzer import analyze_resume
from utils.visualizer import create_score_chart, create_section_breakdown
from datetime import datetime
import base64

# Initialize session state
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'is_first_upload' not in st.session_state:
    st.session_state.is_first_upload = True
if 'selected_resume' not in st.session_state:
    st.session_state.selected_resume = None

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

# Display enhanced logo using SVG
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

# Main container
with st.container():
    # Upload section with improved styling
    st.markdown("### 📤 Upload Your Resume")

    uploaded_file = st.file_uploader("", type=['pdf', 'doc', 'docx'])

    if uploaded_file is not None:
        try:
            with st.spinner('Analyzing your resume...'):
                # Parse and analyze the resume
                resume_text, file_format = parse_resume(uploaded_file)
                analysis_results = analyze_resume(resume_text)

                # Store results
                st.session_state.analysis_results[uploaded_file.name] = analysis_results
                st.session_state.upload_history.append({
                    "filename": uploaded_file.name,
                    "timestamp": datetime.now(),
                    "score": analysis_results['overall_score']
                })
                st.session_state.upload_history = st.session_state.upload_history[-5:]
                st.session_state.selected_resume = uploaded_file.name

        except Exception as e:
            st.error(f"An error occurred while processing your file: {str(e)}")

    # Show recent uploads in collapsible section
    if st.session_state.upload_history:
        with st.expander("📊 Recent Uploads", expanded=st.session_state.is_first_upload):
            for entry in st.session_state.upload_history:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    if st.button(f"📄 {entry['filename']}", key=f"btn_{entry['filename']}"):
                        st.session_state.selected_resume = entry['filename']
                        st.rerun()
                with col2:
                    st.write(entry['timestamp'].strftime("%Y-%m-%d %H:%M"))
                with col3:
                    st.write(f"{entry['score']}%")

        # Set first upload to false after showing the expanded panel
        if st.session_state.is_first_upload:
            st.session_state.is_first_upload = False

    # Display analysis results if a resume is selected
    if st.session_state.selected_resume:
        analysis_results = st.session_state.analysis_results[st.session_state.selected_resume]

        # Results section with enhanced layout
        st.markdown("---")
        st.markdown(f"## 📊 Analysis Results for {st.session_state.selected_resume}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Overall ATS Compliance")
            create_score_chart(analysis_results['overall_score'])

        with col2:
            st.markdown("### Detailed Breakdown")
            create_section_breakdown(analysis_results['section_scores'])

        # HR Quick View with improved styling
        st.markdown("## 💼 HR Quick View")
        hr_snapshot = analysis_results['hr_snapshot']
        quick_stats = hr_snapshot['Quick Stats']

        # Experience and Leadership in cards
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💫 Experience", quick_stats['Experience'])
        with col2:
            st.metric("👥 Leadership", quick_stats['Leadership Indicators'])

        # Education section
        st.markdown("### 🎓 Education Details")
        edu_details = quick_stats['Education']
        if isinstance(edu_details, dict):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Degree", edu_details['level'])
            with col2:
                st.metric("Field", edu_details['major'])
            with col3:
                st.metric("Institution", edu_details['institution'])
        else:
            st.info(edu_details)

        # Skills section with improved layout
        st.markdown("### 🛠️ Skills Profile")
        skills = quick_stats['Skills']
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**💻 Technical**")
            if skills['Technical']:
                for skill in skills['Technical']:
                    st.markdown(f"• {skill.title()}")
            else:
                st.info("No technical skills identified")

        with col2:
            st.markdown("**🤝 Soft Skills**")
            if skills['Soft Skills']:
                for skill in skills['Soft Skills']:
                    st.markdown(f"• {skill.title()}")
            else:
                st.info("No soft skills identified")

        with col3:
            st.markdown("**🔧 Tools & Platforms**")
            if skills['Tools']:
                for tool in skills['Tools']:
                    st.markdown(f"• {tool.title()}")
            else:
                st.info("No tools/platforms identified")

        # Overview section
        st.markdown("## 📋 Key Insights")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ✅ Strengths")
            for impression in hr_snapshot['Initial Impressions']:
                st.markdown(f"• {impression}")

        with col2:
            st.markdown("### ⚠️ Areas for Improvement")
            for flag in hr_snapshot['Potential Red Flags']:
                st.markdown(f"• {flag}")

        # Detailed Analysis Tabs
        st.markdown("## 🔍 Detailed Analysis")
        tabs = st.tabs([
            "Format Analysis",
            "Content Analysis",
            "Recommendations",
            "Raw Data"
        ])

        with tabs[0]:
            st.markdown("### Format Compliance")
            for item in analysis_results['format_analysis']:
                st.markdown(f"• {item}")

        with tabs[1]:
            st.markdown("### Content Analysis")
            for section, details in analysis_results['content_analysis'].items():
                st.markdown(f"**{section}**")
                for detail in details:
                    st.markdown(f"• {detail}")

        with tabs[2]:
            st.markdown("### 🎯 Recommendations for Improvement")

            # High Priority Recommendations
            if analysis_results['recommendations'].get("High Priority"):
                st.markdown("#### ⚠️ Critical Improvements Needed")
                for rec in analysis_results['recommendations']["High Priority"]:
                    with st.expander(f"🔴 {rec['issue']}", expanded=True):
                        st.markdown(f"""
                        **Recommended Action:**  
                        {rec['action']}

                        **Expected Impact:**  
                        {rec['impact']}
                        """)

            # Format Improvements
            if analysis_results['recommendations'].get("Format Improvements"):
                st.markdown("#### 📝 Format Optimization")
                for rec in analysis_results['recommendations']["Format Improvements"]:
                    with st.expander(f"🔸 {rec['issue']}", expanded=False):
                        st.markdown(f"""
                        **Recommended Action:**  
                        {rec['action']}

                        **Expected Impact:**  
                        {rec['impact']}
                        """)

            # Content Enhancements
            if analysis_results['recommendations'].get("Content Enhancements"):
                st.markdown("#### 📈 Content Enhancement")
                for rec in analysis_results['recommendations']["Content Enhancements"]:
                    with st.expander(f"🔹 {rec['issue']}", expanded=False):
                        st.markdown(f"""
                        **Recommended Action:**  
                        {rec['action']}

                        **Expected Impact:**  
                        {rec['impact']}
                        """)

            # Keyword Optimization
            if analysis_results['recommendations'].get("Keyword Optimization"):
                st.markdown("#### 🎯 Keyword Optimization")
                for rec in analysis_results['recommendations']["Keyword Optimization"]:
                    with st.expander(f"📌 {rec['issue']}", expanded=False):
                        st.markdown(f"""
                        **Recommended Action:**  
                        {rec['action']}

                        **Expected Impact:**  
                        {rec['impact']}
                        """)

        with tabs[3]:
            st.markdown("### 📝 Raw Analysis Data")
            st.json(analysis_results)

        # Handle downloads through markdown
        analysis_data = str(analysis_results)
        b64_data = base64.b64encode(analysis_data.encode()).decode()
        st.markdown(f"""
            <div style="display: none;">
                <a id="download_{st.session_state.selected_resume}" 
                   href="data:text/plain;base64,{b64_data}" 
                   download="{st.session_state.selected_resume}_analysis.txt">
                </a>
            </div>""",
            unsafe_allow_html=True
        )

# Handle downloads through markdown (This section is moved inside the if st.session_state.selected_resume block)