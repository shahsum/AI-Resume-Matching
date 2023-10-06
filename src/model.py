import re
import os
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.file_helper import get_resume_text
from src.debugger import print_pipeline

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

# Load spaCy's pre-trained English model
nlp = spacy.load("en_core_web_sm")
skills_nlp = spacy.blank("en")

# create custom entity ruler with training data from https://github.com/kingabzpro/jobzilla_ai/blob/main/jz_skill_patterns.jsonl
ruler = skills_nlp.create_pipe('entity_ruler')
ruler.from_disk("data/skillsets.jsonl")
skills_nlp.add_pipe(ruler)


def process_text(text):
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)

    doc = nlp(text)
    tokens = []

    for token in doc:
        if not token.is_stop and not token.is_punct:
            tokens.append(token.lemma_.lower())

    return tokens

# Tokenize and preprocess text using spaCy and NLTK
def fetch_uniq_skills(jd_tokens):
    job_description = " ".join(jd_tokens)

    doc = skills_nlp(job_description)
    skills = []

    for token in doc.ents:
        if token.label_ == "SKILL":
            skills.append(token.lemma_.lower())
 
    uniq_skills = set(" ".join(skills).split(" "))
    return uniq_skills

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
        "accuracy": 0,
        "common_skills": []
    }

# Function to calculate cosine similarity between two texts
def calculate_cosine_similarity(text1, text2):
    vectors = TfidfVectorizer().fit_transform([text1, text2])
    return cosine_similarity([vectors[0]], [vectors[1]])[0][0]

# Function to match a resume with a job description
def match_resume_with_job_description(resume_text, job_description):
    # Process resume text
    resume_tokens = process_text(resume_text)
    resume_tokens = expand_synonyms(resume_tokens)

    # Preprocess JD
    jd_tokens = process_text(job_description)
    jd_tokens = fetch_uniq_skills(jd_tokens)

    # try to fetch info like email and phone from resume
    info = extract_candidate_info(resume_text)

    # Calculate the percentage of job description skills covered in the resume
    info["common_skills"] = set(jd_tokens).intersection(set(resume_tokens))
    info["accuracy"] = (len(info["common_skills"]) / len(jd_tokens) if len(jd_tokens) > 0 else 0.0)*100

    return info

def match(resume_path, job_description):
    # resume_path = 'resume.pdf'
    # job_description = "Bachelor's or Master’s degree in Computer Science, Engineering or related field, or equivalent training, fellowship, or work experience A track record of approximately 8+ years of solving platform-level problems for multiple teams across the stack by building and delivering production quality software systems Excellent communication skills: Clear written and oral communication is important to our ability to operate as a remote team and in building our relationship with our cross-functional partners Strong sense of ownership and customer empathy: Our mission is to create a seamless customer experience; understanding the intricacies of the customer journey and being proactive about doing right by our customers is critical to our success. Strong engineering fundamentals: we value transferable experience writing & debugging code, scaling existing services, and designing/architecting software systems. Proven expertise in their technology of choice. Ideally full-stack development experience using React, GraphQL, Ruby, Golang, ElasticSearch, and PostgresSQL."
    resume_text = get_resume_text(resume_path)
    data = match_resume_with_job_description(resume_text, job_description)

    print(f"info: {data}")
    return data

# if __name__ == "__main__":
#     match('','')
