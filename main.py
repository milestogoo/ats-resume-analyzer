import streamlit as st
import pandas as pd
from utils.file_parser import parse_resume
from utils.ats_analyzer import analyze_resume
from utils.visualizer import create_score_chart, create_section_breakdown
import base64

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
        
        # Download Report
        report_data = f"""
        ATS Resume Analysis Report
        
        Overall Score: {analysis_results['overall_score']}%
        
        Format Analysis:
        {chr(10).join(analysis_results['format_analysis'])}
        
        Recommendations:
        {chr(10).join([f"{cat}:{chr(10)}" + chr(10).join(recs) 
                       for cat, recs in analysis_results['recommendations'].items()])}
        """
        
        b64 = base64.b64encode(report_data.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="ats_analysis_report.txt">Download Analysis Report</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"An error occurred while processing your file: {str(e)}")
        
else:
    st.info("Please upload a resume to begin the analysis.")
