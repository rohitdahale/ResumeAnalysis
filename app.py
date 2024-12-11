from flask import Flask, request, jsonify
import spacy
import requests
from PyPDF2 import PdfReader

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")  # Load SpaCy NLP model

# Endpoint for resume analysis
@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        # Process the request data
        data = request.json
        resume_url = data.get('resumeUrl')

        if not resume_url:
            return jsonify({"error": "Resume URL is required"}), 400

        # Download and extract text from the resume
        resume_text = download_resume_text(resume_url)

        if not resume_text:
            return jsonify({"error": "Failed to extract text from resume"}), 500

        # Analyze the resume text using SpaCy
        analysis_result = analyze_text_with_spacy(resume_text)

        return jsonify(analysis_result), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Download and extract text from the resume
def download_resume_text(resume_url):
    try:
        # Download the resume as a PDF file
        response = requests.get(resume_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the PDF to a temporary file
        with open("temp_resume.pdf", "wb") as pdf_file:
            pdf_file.write(response.content)

        # Extract text from the PDF
        return extract_text_from_pdf("temp_resume.pdf")

    except Exception as e:
        print(f"Error downloading or reading resume: {e}")
        return None

# Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text.strip()  # Return cleaned-up text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# Analyze the resume text using SpaCy
def analyze_text_with_spacy(resume_text):
    try:
        doc = nlp(resume_text)

        # Extract skills (customize this logic as needed)
        skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]  # Adjust label as per SpaCy's model

        # Generate recommendations based on skills
        recommendations = generate_recommendations(skills)

        return {
            "skills": skills,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error analyzing text with SpaCy: {e}")
        return {"skills": [], "recommendations": []}

# Generate recommendations based on extracted skills
def generate_recommendations(skills):
    recommendations = []
    if "Python" in skills:
        recommendations.append("Take an advanced Python programming course.")
    if "Machine Learning" in skills:
        recommendations.append("Explore a machine learning specialization.")
    if not recommendations:
        recommendations.append("Enhance your skills with relevant courses or certifications.")
    return recommendations

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
