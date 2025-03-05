# ATS Resume Analyzer

A modern, AI-powered Applicant Tracking System (ATS) compliance analyzer that helps job seekers optimize their resumes for better visibility and success.

## Features

- 📄 Multi-format Resume Parsing (PDF, DOC, DOCX)
- 📊 Comprehensive ATS Compliance Scoring
- 🎯 Detailed Section-wise Analysis
- 💼 HR Quick View with Experience & Skills Breakdown
- 📈 Visual Compliance Metrics
- 🔍 Keyword Optimization Suggestions
- 🎨 Modern, Clean UI with Blue Theme

## Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Python, Pandas
- **PDF Processing**: PyPDF2
- **Document Processing**: python-docx
- **Visualization**: Plotly

## Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/ats-resume-analyzer.git
cd ats-resume-analyzer
```

2. Install dependencies:
```bash
pip install streamlit pandas plotly pypdf2 python-docx
```

3. Create the required directories:
```bash
mkdir -p .streamlit assets
```

4. Run the application:
```bash
streamlit run main.py
```

## Usage

1. Launch the application using `streamlit run main.py`
2. Upload your resume in PDF, DOC, or DOCX format
3. Review the comprehensive analysis including:
   - Overall ATS compliance score
   - Section-wise breakdown
   - HR snapshot with experience and skills analysis
   - Detailed recommendations for improvement

## Project Structure

```
.
├── assets/
│   └── style.css         # Custom styling
├── utils/
│   ├── ats_analyzer.py   # Core analysis logic
│   ├── file_parser.py    # File parsing utilities
│   └── visualizer.py     # Data visualization components
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── main.py              # Main application file
```

## Features in Detail

### Resume Analysis
- Comprehensive parsing of PDF and Word documents
- Extraction of key sections: contact info, experience, education, skills
- Pattern matching for dates, achievements, and leadership indicators

### Scoring System
- Overall ATS compliance score
- Section-wise breakdown
- Format and keyword analysis
- Content quality assessment

### HR Quick View
- Experience timeline estimation
- Education level detection
- Skills categorization
- Leadership indicators

### Visual Analytics
- Interactive charts and metrics
- Section-wise score breakdown
- Progress indicators
- Modern, responsive design

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit
- Styling inspired by modern design principles
- Resume parsing based on industry standard ATS systems