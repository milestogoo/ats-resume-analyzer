import PyPDF2
from docx import Document
import io

def parse_resume(uploaded_file):
    """
    Parse uploaded resume file and extract text content
    """
    file_type = uploaded_file.name.split('.')[-1].lower()
    content = ""
    
    try:
        if file_type == 'pdf':
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                content += page.extract_text()
                
        elif file_type in ['doc', 'docx']:
            doc = Document(io.BytesIO(uploaded_file.read()))
            for para in doc.paragraphs:
                content += para.text + "\n"
                
        return content.strip(), file_type
        
    except Exception as e:
        raise Exception(f"Error parsing {file_type.upper()} file: {str(e)}")
