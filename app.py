from sentence_transformers import SentenceTransformer, util
from flask import Flask, render_template, request
import spacy
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "we",
    "with", "you", "your", "our", "will", "this", "they", "their",
    "someone", "looking", "data", "skill", "skills", "role", "candidate",
    "experience", "work", "job", "description", "looking", "required", 
    "requirement", "requirements", "company", "day", "team", "role", 
    "responsibility", "business", "client", "work", "environment",
    "company", "day", "business", "client", "account", "active", "administer",
    "cert", "certification", "change", "clean", "clear", "base", "diverse",
    "fundamental", "issue", "management", "opportunity", "platform",
    "responsibilities", "responsibility", "professional", "support",
    "service", "services", "process", "processes", "system", "systems",
    "ability", "access", "advisor", "agent", "architecture", "organization",
    "position", "employee", "employer", "department", "individual", "candidate"
}

KNOWN_SKILLS = {
    "python", "sql", "flask", "javascript", "github", "git", "vs code",
    "machine learning", "nlp", "computer vision", "data analysis",
    "data cleaning", "visualization", "statistical modeling",
    "windows", "microsoft 365", "active directory", "entra id",
    "dns", "dhcp", "vpn", "firewall", "networking", "powershell",
    "comptia", "security", "helpdesk", "ticketing", "documentation",
    "communication", "teamwork", "project management", "deployment"
}

SKILL_CATEGORIES = {
    "Technical Skills": {
        "python", "sql", "flask", "javascript",
        "networking", "dns", "dhcp", "vpn",
        "firewall", "powershell", "windows",
        "microsoft 365", "active directory",
        "entra id"
    },

    "Soft Skills": {
        "communication", "teamwork",
        "project management"
    }
}

def extract_keywords(text: str):
    text_lower = text.lower()
    doc = nlp(text_lower)
    keywords = set()

    for skill in KNOWN_SKILLS:
        if skill in text_lower:
            keywords.add(skill)

    for token in doc:
        if (
            token.is_alpha
            and not token.is_stop
            and token.text not in STOP_WORDS
            and len(token.text) > 2
            and token.pos_ in {"NOUN", "PROPN"}
        ):
            keyword = token.lemma_.strip()
            if keyword not in STOP_WORDS and len(keyword) > 2:
                keywords.add(keyword)

    return keywords

def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "

        return text.strip()
    except Exception:
        return ""

def extract_text_from_docx(file):
    try:
        document = Document(file)
        text = ""

        for paragraph in document.paragraphs:
            if paragraph.text:
                text += paragraph.text + " "

        return text.strip()
    except Exception:
        return "" 
    
#test test test
def calculate_match_score(common_words, job_words):
    if not job_words:
        return 0

    base_score = int((len(common_words) / len(job_words)) * 100)

    known_skill_matches = common_words.intersection(KNOWN_SKILLS)

    bonus_score = len(known_skill_matches) * 6

    final_score = base_score + bonus_score

    return min(final_score, 100)

def calculate_semantic_similarity(resume_text: str, job_text: str):
    if len(resume_text.strip()) < 10 or len(job_text.strip()) < 10:
        return 0

    resume_embedding = semantic_model.encode(resume_text, convert_to_tensor=True)
    job_embedding = semantic_model.encode(job_text, convert_to_tensor=True)

    similarity = util.cos_sim(resume_embedding, job_embedding).item()

    return int(similarity * 100)

def analyze_match(resume_text: str, job_text: str):
    resume_words = extract_keywords(resume_text)
    job_words = extract_keywords(job_text)

    common_words = resume_words.intersection(job_words)
    missing_words = job_words.difference(resume_words)

    match_score = calculate_match_score(common_words, job_words)
    semantic_score = calculate_semantic_similarity(resume_text, job_text)
    overall_score = int((match_score * 0.6) + (semantic_score * 0.4))
    matched_groups = group_skills(common_words)

    if overall_score >= 70:
            match_label = "Strong Match"
            match_explanation = "This resume is a strong match because it has strong keyword overlap and similar meaning to the job description."
    elif overall_score >= 40:
            match_label = "Moderate Match"
            match_explanation = "This resume has some overlap with the job description, but there are still important skills or concepts missing."
    else:
            match_label = "Low Match"
            match_explanation = "This resume has limited overlap with the job description and may need more targeted skills or experience."

    suggestions = [
        f"Add experience related to {word} to improve your match."
        for word in sorted(list(missing_words))[:5]
    ]

    return {
        "match_score": overall_score,
        "keyword_score": match_score,
        "semantic_score": semantic_score,
        "match_label": match_label,
        "matched_skills": sorted(list(common_words))[:10],
        "missing_skills": sorted(list(missing_words))[:10],
        "match_explanation": match_explanation,
        "suggestions": suggestions,
        "matched_groups": matched_groups,
    }

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = request.form.get('resume_text', '')
    job_text = request.form.get('job_text', '')

    uploaded_file = request.files.get('resume_file')

    # if a file is uploaded, use it instead of text
    if uploaded_file:
        filename = uploaded_file.filename.lower()

        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(uploaded_file)

        elif filename.endswith('.docx'):
            resume_text = extract_text_from_docx(uploaded_file)

    if len(resume_text.strip()) < 10 or len(job_text.strip()) < 10:
        return render_template(
        'results.html',
        match_score=0,
        keyword_score=0,
        semantic_score=0,
        match_label="Not Enough Information",
        match_explanation="Please enter a longer resume and job description so FitCheck can analyze the match properly.",
        matched_skills=[],
        missing_skills=[],
        suggestions=["Add more resume and job description text before analyzing."]
    )

    results = analyze_match(resume_text, job_text)

    return render_template(
        'results.html',
        match_score=results["match_score"],
        keyword_score=results["keyword_score"],
        semantic_score=results["semantic_score"],
        match_label=results["match_label"],
        matched_skills=results["matched_skills"],
        missing_skills=results["missing_skills"],
        suggestions=results["suggestions"],
        match_explanation=results["match_explanation"],
    )

def group_skills(skills):
    grouped = {}

    for category, category_skills in SKILL_CATEGORIES.items():
        matches = sorted([
            skill for skill in skills
            if skill in category_skills
        ])

        if matches:
            grouped[category] = matches

    return grouped

if __name__ == '__main__':
    app.run(debug=True)