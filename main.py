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
if 'is_first_upload' not in st.session_state:
    st.session_state.is_first_upload = True

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

# Create a grid of UI inspirations using st.columns
st.markdown("## 💫 UI Design Inspirations")

# Create three columns for the mockups
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, #1E88E5, #1565C0); border-radius: 15px; color: white;">
        <h3 style="color: white;">Modern Blue</h3>
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; color: #1565C0;">
            <div style="height: 10px; width: 60%; background: #E3F2FD; border-radius: 5px; margin: 5px 0;"></div>
            <div style="height: 10px; width: 80%; background: #E3F2FD; border-radius: 5px; margin: 5px 0;"></div>
        </div>
        <p style="color: #E3F2FD; font-size: 0.9em;">Clean, professional design with strong emphasis on readability</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, #0288D1, #01579B); border-radius: 15px; color: white;">
        <h3 style="color: white;">Deep Ocean</h3>
        <div style="background: #F5F9FF; padding: 15px; border-radius: 10px; margin: 10px 0; color: #01579B;">
            <div style="height: 10px; width: 70%; background: #E1F5FE; border-radius: 5px; margin: 5px 0;"></div>
            <div style="height: 10px; width: 90%; background: #E1F5FE; border-radius: 5px; margin: 5px 0;"></div>
        </div>
        <p style="color: #B3E5FC; font-size: 0.9em;">Rich, deep colors with excellent contrast for key information</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, #039BE5, #0277BD); border-radius: 15px; color: white;">
        <h3 style="color: white;">Crystal Clear</h3>
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; color: #0277BD;">
            <div style="height: 10px; width: 75%; background: #F5F9FF; border-radius: 5px; margin: 5px 0;"></div>
            <div style="height: 10px; width: 85%; background: #F5F9FF; border-radius: 5px; margin: 5px 0;"></div>
        </div>
        <p style="color: #E1F5FE; font-size: 0.9em;">Bright and airy design with subtle depth effects</p>
    </div>
    """, unsafe_allow_html=True)

# Add color palette section
st.markdown("### 🎨 Color Palettes")

# Create two columns for the color palettes
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="padding: 20px; background: white; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4>Professional Blue</h4>
        <div style="display: flex; gap: 10px; margin: 10px 0;">
            <div style="background: #0277BD; width: 50px; height: 50px; border-radius: 8px;"></div>
            <div style="background: #01579B; width: 50px; height: 50px; border-radius: 8px;"></div>
            <div style="background: #F5F9FF; width: 50px; height: 50px; border-radius: 8px; border: 1px solid #E1F5FE;"></div>
            <div style="background: #FFFFFF; width: 50px; height: 50px; border-radius: 8px; border: 1px solid #E1F5FE;"></div>
        </div>
        <p style="color: #666; font-size: 0.9em;">Primary: #0277BD<br>Secondary: #01579B<br>Background: #F5F9FF</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="padding: 20px; background: white; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4>Ocean Depths</h4>
        <div style="display: flex; gap: 10px; margin: 10px 0;">
            <div style="background: #039BE5; width: 50px; height: 50px; border-radius: 8px;"></div>
            <div style="background: #0288D1; width: 50px; height: 50px; border-radius: 8px;"></div>
            <div style="background: #E1F5FE; width: 50px; height: 50px; border-radius: 8px; border: 1px solid #B3E5FC;"></div>
            <div style="background: #FFFFFF; width: 50px; height: 50px; border-radius: 8px; border: 1px solid #B3E5FC;"></div>
        </div>
        <p style="color: #666; font-size: 0.9em;">Primary: #039BE5<br>Secondary: #0288D1<br>Background: #E1F5FE</p>
    </div>
    """, unsafe_allow_html=True)

# Add UI Elements section
st.markdown("### 🎯 Key UI Elements")

# Create three columns for UI elements
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="padding: 20px; background: white; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4>Cards & Containers</h4>
        <div style="background: #F5F9FF; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <div style="height: 40px; background: white; border-radius: 8px; margin: 5px 0; border: 1px solid #E1F5FE;"></div>
            <div style="height: 40px; background: white; border-radius: 8px; margin: 5px 0; border: 1px solid #E1F5FE;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="padding: 20px; background: white; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4>Metrics & Stats</h4>
        <div style="background: #F5F9FF; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <div style="height: 20px; width: 80%; background: #0277BD; border-radius: 10px; margin: 10px 0;"></div>
            <div style="height: 20px; width: 60%; background: #01579B; border-radius: 10px; margin: 10px 0;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="padding: 20px; background: white; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4>Interactive Elements</h4>
        <div style="background: #F5F9FF; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <div style="height: 40px; background: #0277BD; border-radius: 8px; margin: 10px 0; display: flex; align-items: center; justify-content: center; color: white;">Button</div>
            <div style="height: 40px; background: white; border-radius: 8px; margin: 10px 0; border: 2px dashed #0277BD;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("Select your preferred design inspiration, and we can implement the chosen style throughout the application.")


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

            # Show recent uploads in collapsible section
            if st.session_state.upload_history:
                # Expand the panel on first upload
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

                # Set first upload to false after showing the expanded panel
                if st.session_state.is_first_upload:
                    st.session_state.is_first_upload = False

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