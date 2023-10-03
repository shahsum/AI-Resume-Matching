import os
import re
import spacy
import docx2txt
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet

# Create a synonym dictionary
synonym_dict = {
    "ML": ["machine learning"],
    "analysis": ["analytics"],
    "ror": ["ruby", "Ruby on Rails"],
    "ruby": ["ruby", "Ruby on Rails"],
    "JavaScript": ["JS", "Java Script"],
    "js": ["JS", "Java Script"],
    "React": ["ReactJS", "react.js"]
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
def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text).replace("\n", " ")
    doc = nlp(text)
    tokens = []

    # Define entity types to be removed (e.g., PERSON, GPE for city, ADDRESS, EMAIL)
    entities_to_remove = ["PERSON", "GPE", "ADDRESS", "EMAIL"]

    for token in doc:
        # Check if the token's entity type is not in the list of entities to remove
        # print(token.ent_type_)
        # print(token.text)
        if token.ent_type_ not in entities_to_remove and not token.is_stop and not token.is_punct:
            tokens.append(token.lemma_.lower())
            
    array = expand_synonyms(tokens)
    return " ".join(array)

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
    # Initialize variables to store extracted information
    candidate_email = ""
    candidate_phone = ""

    # Regular expression patterns for email and phone number extraction
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
        "Email": candidate_email,
        "Phone": candidate_phone,
    }

# Function to calculate cosine similarity between two texts
def calculate_cosine_similarity(text1, text2):
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    return cosine_similarity([vectors[0]], [vectors[1]])[0][0]

# Function to match a resume with a job description
def match_resume_with_job_description(resume_text, job_description):
    # Preprocess the text
    resume_text = preprocess_text(resume_text)
    job_description = preprocess_text(job_description)

    # Calculate cosine similarity between the resume and job description
    similarity_score = calculate_cosine_similarity(resume_text, job_description)

    return similarity_score

# Function to calculate coverage score
def calculate_coverage_score(resume_text, job_description):
    # Tokenize the job description into keywords or phrases
    job_keywords = job_description.lower().split()

    # Tokenize and preprocess the resume text
    resume_tokens = preprocess_text(resume_text)

    # Calculate the number of job keywords that appear in the resume
    keywords_found = sum(1 for keyword in job_keywords if keyword in resume_tokens)

    # Calculate the coverage score as a percentage
    coverage_score = (keywords_found / len(job_keywords)) * 100

    return coverage_score

if __name__ == "__main__":
    resume_path = 'resume.pdf'
    job_description = "Bachelor's or Master’s degree in Computer Science, Engineering or related field, or equivalent training, fellowship, or work experience A track record of approximately 8+ years of solving platform-level problems for multiple teams across the stack by building and delivering production quality software systems Excellent communication skills: Clear written and oral communication is important to our ability to operate as a remote team and in building our relationship with our cross-functional partners Strong sense of ownership and customer empathy: Our mission is to create a seamless customer experience; understanding the intricacies of the customer journey and being proactive about doing right by our customers is critical to our success. Strong engineering fundamentals: we value transferable experience writing & debugging code, scaling existing services, and designing/architecting software systems. Proven expertise in their technology of choice. Ideally full-stack development experience using React, GraphQL, Ruby, Golang, ElasticSearch, and PostgresSQL."
    resume_text = get_resume_text(resume_path)

    # fetch email and phone
    info = extract_candidate_info(resume_text)
    print(f"Candidate Info: {info}")

    similarity_score = match_resume_with_job_description(resume_text, job_description)
    print(f"Similarity Score: {similarity_score}")

    coverage_score = calculate_coverage_score(resume_text, job_description)
    print(f"JD Coverage Score: {coverage_score}%")

