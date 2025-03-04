import PyPDF2
from docx import Document
import io

def parse_resume(uploaded_file):
    """
    Parse uploaded resume file and extract text content
    Returns a tuple of (text_content, file_type)
    """
    if uploaded_file is None:
        raise ValueError("No file was uploaded")

    file_type = uploaded_file.name.split('.')[-1].lower()
    content = []

    try:
        if file_type == 'pdf':
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content.append(page_text)

        elif file_type in ['doc', 'docx']:
            doc = Document(io.BytesIO(uploaded_file.read()))
            content = [para.text for para in doc.paragraphs if para.text.strip()]

        # Join all content into a single string
        text_content = '\n'.join(content)

        # Validate extracted content
        if not text_content.strip():
            raise ValueError("No text content could be extracted from the file")

        return text_content.strip(), file_type

    except Exception as e:
        raise Exception(f"Error parsing {file_type.upper()} file: {str(e)}")