import docx2txt
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup

# Function to extract text from a DOCX file
def extract_text_from_docx(docx_path):
    text = docx2txt.process(docx_path)
    return text

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

# Function to extract text from an HTML file
def extract_text_from_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        text = soup.get_text()
    return text

def get_resume_text(resume_path):
    resume_text = ''
    # Extract text from the resume
    if resume_path.endswith('.docx'):
        resume_text = extract_text_from_docx(resume_path)
    elif resume_path.endswith('.pdf'):
        resume_text = extract_text_from_pdf(resume_path)
    elif resume_path.endswith('.html'):
        resume_text = extract_text_from_html(resume_path)
    else:
        os.remove(resume_path)
        raise ValueError("Unsupported resume format")
    return resume_text