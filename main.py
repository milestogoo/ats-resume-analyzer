import streamlit as st
import pandas as pd
from utils.file_parser import parse_resume
from utils.ats_analyzer import analyze_resume
from utils.visualizer import create_score_chart, create_section_breakdown
from datetime import datetime
import base64

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

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
                    <stop offset="100%" style="stop-color:#2196F3"/>
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
    st.markdown("_Supported formats: PDF, DOC, DOCX_")

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

            # Show recent uploads in collapsible section
            if st.session_state.upload_history:
                with st.expander("📊 Recent Uploads", expanded=False):
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

            # Results section with enhanced layout
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")

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
                st.markdown("### Recommendations")
                for category, recommendations in analysis_results['recommendations'].items():
                    st.markdown(f"**{category}**")
                    for rec in recommendations:
                        st.markdown(f"• {rec}")

            with tabs[3]:
                st.markdown("### 📝 Raw Analysis Data")
                st.json(analysis_results)

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