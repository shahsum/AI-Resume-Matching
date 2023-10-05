from flask import Flask, render_template, request
from model import match
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Define a route to render the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# Define a route to handle form submission
@app.route('/match', methods=['POST'])
def match_resume():
    resume_file = request.files['resume']
    job_description = request.form['job_description']

    # Check if a file was uploaded
    if resume_file:
        # Save the uploaded file to a specified directory
        resume_filename = secure_filename(resume_file.filename)
        resume_file.save(os.path.join('uploads', resume_filename))

        # Process the resume and job description here (use the functions from the previous example)
        # similarity_score = match_resume_with_job_description(resume_filepath, job_description)
        resume_filepath = os.path.join('uploads', resume_filename)
        similarity_score = match(resume_filepath, job_description)

        # Delete the uploaded file after processing (optional)
        os.remove(resume_filepath)

        return render_template('result.html', similarity_score=similarity_score)
    else:
        # Handle the case where no file was uploaded
        return "No resume file uploaded."
    
@app.errorhandler(Exception)
def internal_server_error(error):
    return render_template('error.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
