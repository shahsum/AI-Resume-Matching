import re
import spacy
# from spacy import displacy
import docx2txt
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet

# Create a synonym dictionary
synonym_dict = {
    "ml": ["machine learning"],
    "analysis": ["analytics"],
    "ror": ["ruby", "ruby on rails"],
    "ruby": ["ruby", "ruby on rails"],
    "javascript": ["js", "java script", "ecmascript", "client-side scripting"],
    "js": ["js", "java script", "ecmascript", "client-side scripting"],
    "react": ["reactjs", "react.js"]
    # Add more synonyms as needed
}

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

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
        raise ValueError("Unsupported resume format")
    return resume_text

# Tokenize and preprocess text using spaCy and NLTK
def preprocess_jd(job_description):
    job_description = job_description.replace("\n", " ")
    job_description = re.sub(r'\s+', ' ', job_description)

    doc = nlp(job_description)
    tokens = []

    # Define the relevant part-of-speech tags and dependency labels
    relevant_pos_tags = ["NOUN", "PROPN", "ADJ"]
    relevant_dependency_labels = ["amod", "compound", "nsubj", "attr", "conj"]

    for token in doc:
        if (token.pos_ in relevant_pos_tags or token.dep_ in relevant_dependency_labels) and not token.is_stop and not token.is_punct:
            tokens.append(token.lemma_.lower())
 
    return tokens

# Tokenize and preprocess text using spaCy and NLTK
def preprocess_resume_text(resume_text):
    resume_text = resume_text.replace("\n", " ")
    resume_text = re.sub(r'\s+', ' ', resume_text)

    doc = nlp(resume_text)
    # displacy.serve(doc, style="dep", port=5001)
    tokens = []

    for token in doc:
        tokens.append(token.lemma_.lower())
 
    return expand_synonyms(tokens)

# Function to expand synonyms
def expand_synonyms(tokens):
    expanded_tokens = []
    for token in tokens:
        expanded_tokens.append(token)
        if token in synonym_dict:
            expanded_tokens.extend(synonym_dict[token])
    return expanded_tokens

# Function to extract candidate information from a resume
def extract_candidate_info(text):
    candidate_email = ""
    candidate_phone = ""

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    phone_pattern = r'\b(?:\+\d{1,2}\s?)?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{4}\b'

    # Extract email using regex
    email_match = re.search(email_pattern, text)
    if email_match:
        candidate_email = email_match.group()

    # Extract phone number using regex
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        candidate_phone = phone_match.group()

    return {
        "email": candidate_email,
        "phone": candidate_phone,
        "accuracy": 0
    }

# Function to calculate cosine similarity between two texts
def calculate_cosine_similarity(text1, text2):
    vectors = TfidfVectorizer().fit_transform([text1, text2])
    return cosine_similarity([vectors[0]], [vectors[1]])[0][0]

# Function to match a resume with a job description
def match_resume_with_job_description(resume_text, job_description):
     # Preprocess and tokenize the text
    jd_tokens = preprocess_jd(job_description)
    resume_tokens = preprocess_resume_text(resume_text)
    resume_tokens = expand_synonyms(resume_tokens)

    # Calculate the percentage of job description skills covered in the resume
    common_tokens = set(jd_tokens).intersection(set(resume_tokens))
    print(common_tokens)
    percentage_covered = len(common_tokens) / len(jd_tokens) if len(jd_tokens) > 0 else 0.0

    return percentage_covered * 100

def match(resume_path, job_description):
    # resume_path = 'resume.pdf'
    # job_description = "Bachelor's or Master’s degree in Computer Science, Engineering or related field, or equivalent training, fellowship, or work experience A track record of approximately 8+ years of solving platform-level problems for multiple teams across the stack by building and delivering production quality software systems Excellent communication skills: Clear written and oral communication is important to our ability to operate as a remote team and in building our relationship with our cross-functional partners Strong sense of ownership and customer empathy: Our mission is to create a seamless customer experience; understanding the intricacies of the customer journey and being proactive about doing right by our customers is critical to our success. Strong engineering fundamentals: we value transferable experience writing & debugging code, scaling existing services, and designing/architecting software systems. Proven expertise in their technology of choice. Ideally full-stack development experience using React, GraphQL, Ruby, Golang, ElasticSearch, and PostgresSQL."
    resume_text = get_resume_text(resume_path)

    # fetch email and phone
    info = extract_candidate_info(resume_text)

    info["accuracy"] = match_resume_with_job_description(resume_text, job_description)
    print(f"info: {info}")
    return info

# if __name__ == "__main__":
#     match('','')
