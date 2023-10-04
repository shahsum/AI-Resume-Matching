from flask import Flask, render_template, request
from model import match
import os

app = Flask(__name__)

# Define a route to render the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# Define a route to handle form submission
@app.route('/match', methods=['POST'])
def match_resume():
    resume = request.form['resume']
    job_description = request.form['job_description']
    print(resume)
    print(job_description)

    # Process the resume and job description here (use the functions from the previous example)
    # similarity_score = match_resume_with_job_description(resume, job_description)

    similarity_score = match(resume, job_description)
    print(similarity_score)
    return render_template('result.html', similarity_score=similarity_score)

if __name__ == '__main__':
    app.run(debug=True)
