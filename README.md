# ATS Resume Analyzer

A modern, AI-powered Applicant Tracking System (ATS) compliance analyzer that helps job seekers optimize their resumes for better visibility and success.

## Live Demo
Access the live application at: [ATS Resume Analyzer](https://ats-resume-analyzer.replit.app)

## Features

- 📄 Multi-format Resume Parsing (PDF/DOC/DOCX)
- 📊 Comprehensive ATS Compliance Scoring
- 🎯 Detailed Section-wise Analysis
- 💼 HR Quick View with Experience & Skills Breakdown
- 📈 Visual Compliance Metrics
- 🔍 Keyword Optimization Suggestions
- 🎨 Modern, Clean UI with Blue Theme

## Dependencies

Required Python packages:
```
streamlit
pandas
plotly
pypdf2
python-docx
reportlab
```

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/ats-resume-analyzer.git
cd ats-resume-analyzer
```

2. Install dependencies:
```bash
pip install streamlit pandas plotly pypdf2 python-docx reportlab
```

3. Run the application:
```bash
streamlit run main.py
```

## Project Structure

```
.
├── assets/
│   └── style.css         # Custom styling
├── utils/
│   ├── ats_analyzer.py   # Core analysis logic
│   ├── file_parser.py    # File parsing utilities
│   ├── pdf_generator.py  # PDF report generation
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

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository.