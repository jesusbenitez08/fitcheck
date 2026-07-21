from sentence_transformers import SentenceTransformer, util
from flask import Flask, render_template, request
import spacy
import sqlite3
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document
import csv
from flask import send_file


app = Flask(__name__)
DATABASE = "fitcheck_results.db"
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
    "position", "employee", "employer", "department", "individual", "candidate",
    "required experience",
    "minimum qualifications", "equal opportunity", "job description", "our company",
    "the team", "your role", "what we offer", "ideal candidate",
}

BAD_PHRASES = {
    "professional experience",
    "qualified candidate",
    "ideal candidate",
    "job description",
    "minimum qualifications",
    "equal opportunity",
    "our company",
    "the team",
    "your role",
    "what we offer",
    "business needs",
    "company culture",
    "work environment",
    "day-to-day",
    "strong ability",
    "excellent communication",
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
            keywords.add(skill.title())

    #testing to extract useful noun phrases
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        words = phrase.split()

        if len(phrase) < 3:
            continue

        if phrase in STOP_WORDS or phrase in BAD_PHRASES:
            continue

        if len(words) > 5:
            continue

        if any(word in STOP_WORDS for word in words):
            continue

        useful_tokens = [
            token for token in chunk
            if token.pos_ in {"NOUN", "PROPN", "ADJ"}
            and not token.is_stop
        ]

        if len(useful_tokens) < 1:
            continue

        keywords.add(phrase.title())

    for token in doc:
        if (
            token.is_alpha
            and not token.is_stop
            and token.pos_ in {"NOUN", "PROPN"}
            and len(token.text) > 2
        ):
            lemma = token.lemma_.lower()

            if lemma in STOP_WORDS or lemma in BAD_PHRASES:
                continue

            keywords.add(lemma.title())

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


def filter_display_skills(skills):
    blocked_words = {
        "ability", "activity", "advancement", "agency", "approach",
        "audience", "bachelor", "benefit", "build", "comfort",
        "culture", "desire", "destination", "employee", "employer",
        "goal", "individual", "license", "mindset", "need",
        "opportunity", "organization", "package", "position"
    }

    cleaned_skills = []

    for skill in skills:
        if skill in blocked_words:
            continue

        if len(skill) <= 2:
            continue

        cleaned_skills.append(skill)

    return sorted(cleaned_skills)

def group_missing_concepts(missing_skills):
    concepts = {
        "technical tools or platforms": {
            "python", "sql", "flask", "javascript", "github", "git",
            "microsoft 365", "active directory", "entra id", "dns",
            "dhcp", "vpn", "firewall", "networking", "powershell"
        },
        "communication and collaboration": {
            "communication", "teamwork", "collaboration", "interpersonal",
            "presentation", "customer service"
        },
        "analysis and reporting": {
            "data analysis", "visualization", "statistical modeling",
            "reporting", "dashboard", "insights", "metrics"
        },
        "healthcare or clinical experience": {
            "patient care", "assessment", "care planning", "documentation",
            "compliance", "healthcare", "clinical"
        },
        "sales and customer engagement": {
            "sales", "crm", "negotiation", "lead generation",
            "closing", "prospecting", "relationship building"
        }
    }

    matched_concepts = []

    for concept, keywords in concepts.items():
        if any(skill in keywords for skill in missing_skills):
            matched_concepts.append(concept)

    return matched_concepts


def generate_ai_summary(score, matched, missing):

    if score >= 80:
        intro = "Your resume aligns very well with this position."
    elif score >= 65:
        intro = "Your resume is a strong match, but there are still opportunities to strengthen it."
    elif score >= 45:
        intro = "Your resume has a solid foundation, but adding more relevant experience could improve your match."
    else:
        intro = "Your resume currently matches only part of what this role is looking for."

    summary = intro

    if matched:
        summary += (
            f" Your strongest qualifications appear to be "
            f"{', '.join(matched[:4])}."
        )

    if missing:
        summary += (
            f" The biggest opportunities for improvement are "
            f"{', '.join(missing[:4])}."
        )

    if score >= 80:
        summary += (
            " You should be competitive for this position with only minor adjustments."
        )

    elif score >= 65:
        summary += (
            " Tailoring your resume toward these areas could increase your chances of passing an ATS screening."
        )

    elif score >= 45:
        summary += (
            " Adding measurable accomplishments and projects related to these topics could significantly strengthen your resume."
        )

    else:
        summary += (
            " Consider revising your resume to better reflect the skills and experience requested in the job description."
        )

    return summary

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_name TEXT,
            match_score INTEGER,
            keyword_score INTEGER,
            semantic_score INTEGER,
            match_label TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_analysis_result(resume_name, results):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis_results (
            resume_name,
            match_score,
            keyword_score,
            semantic_score,
            match_label,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        resume_name,
        results["match_score"],
        results["keyword_score"],
        results["semantic_score"],
        results["match_label"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

def filter_job_description(job_text: str):
    important_headers = [
        "requirements",
        "qualifications",
        "responsibilities",
        "key responsibilities",
        "skills",
        "experience",
        "what you need",
        "what you'll do",
        "job duties"
    ]

    ignore_headers = [
        "benefits",
        "what we offer",
        "about us",
        "overview",
        "company culture",
        "schedule",
        "pay",
        "compensation"
    ]

    lines = job_text.splitlines()
    filtered_lines = []
    keep_section = True

    for line in lines:
        clean_line = line.strip().lower()

        if not clean_line:
            continue

        if any(header in clean_line for header in important_headers):
            keep_section = True
            continue

        if any(header in clean_line for header in ignore_headers):
            keep_section = False
            continue

        if keep_section:
            filtered_lines.append(line)

    filtered_text = " ".join(filtered_lines)

    if len(filtered_text.strip()) < 20:
        return job_text

    return filtered_text

GENERIC_TERMS = {
    "company",
    "organization",
    "team",
    "role",
    "position",
    "marketplace",
    "market",
    "client",
    "customers",
    "customer",
    "business",
    "deloitte",
    "professional",
    "opportunity",
    "environment",
    "today",
    "work",
    "working",
    "candidate",
    "experience",
    "years",
    "year",
    "ability",
    "information",
    "technology",
    "computer",
    "science",
    "development",
    "completion",
    "concept",
    "award",
    "case",
    "accuracy",
}


def merge_similar_skills(skills):
    sorted_skills = sorted(skills, key=len, reverse=True)
    merged = []

    for skill in sorted_skills:
        skill_lower = skill.lower()
        should_keep = True

        for existing in merged:
            existing_lower = existing.lower()

            if skill_lower in existing_lower:
                should_keep = False
                break

        if should_keep:
            merged.append(skill)

    return merged

def rank_skills_by_relevance(skills, comparison_text, top_n=8):
    if not skills or len(comparison_text.strip()) < 10:
        return []

    skill_list = merge_similar_skills(skills)

    comparison_embedding = semantic_model.encode(
        comparison_text,
        convert_to_tensor=True
    )

    ranked_skills = []

    for skill in skill_list:

        if (
            len(skill) < 3
            or skill.lower() in GENERIC_TERMS
        ):
            continue

        if len(skill.split()) > 5:
            continue

        skill_embedding = semantic_model.encode(
            skill,
            convert_to_tensor=True
        )

        similarity = util.cos_sim(skill_embedding, comparison_embedding).item()

        ranked_skills.append((skill, similarity))

    ranked_skills.sort(key=lambda item: item[1], reverse=True)

    seen = set()
    final_skills = []

    for skill, score in ranked_skills:

        lower = skill.lower()

        if lower not in seen:
            seen.add(lower)
            final_skills.append(skill)

    return final_skills[:top_n]


def analyze_match(resume_text: str, job_text: str):
    filtered_job_text = filter_job_description(job_text)

    resume_words = extract_keywords(resume_text)
    job_words = extract_keywords(filtered_job_text)
    
    

    common_words = resume_words.intersection(job_words)
    missing_words = job_words.difference(resume_words)
    display_matched_skills = rank_skills_by_relevance(
        common_words,
        filtered_job_text
    )

    display_missing_skills = rank_skills_by_relevance(
        missing_words,
        resume_text
    )

    cleaned_missing = []

    matched_lower = [skill.lower() for skill in display_matched_skills]

    for skill in display_missing_skills:

        skill_lower = skill.lower()

        overlap = False

        for matched in matched_lower:
            if matched in skill_lower or skill_lower in matched:
                overlap = True
                break

        if not overlap:
            cleaned_missing.append(skill)

    display_missing_skills = cleaned_missing

    match_score = calculate_match_score(common_words, job_words)
    semantic_score = calculate_semantic_similarity(resume_text, filtered_job_text)
    overall_score = int((match_score * 0.25) + (semantic_score * 0.75))

    if semantic_score >= 45 and overall_score < 45:
        overall_score = 45

    if semantic_score >= 60 and overall_score < 55:
        overall_score = 55

    if semantic_score >= 70 and overall_score < 65:
        overall_score = 65
            
    matched_groups = group_skills(common_words)

    if overall_score >= 65:
            match_label = "Strong Match"
            match_explanation = "This resume is a strong match because it has strong keyword overlap and similar meaning to the job description."

    elif overall_score >= 40:
            match_label = "Moderate Match"
            match_explanation = "This resume has some overlap with the job description, but there are still important skills or concepts missing."

    else:
            match_label = "Low Match"
            match_explanation = "This resume has limited overlap with the job description and may need more targeted skills or experience."

    
    suggestions = [
        f"Consider adding more detail about {skill} if it is relevant to your background."
        for skill in display_missing_skills[:3]
    ]

    if not suggestions:
        suggestions = ["No major skill gaps were identified from the current analysis."]
    
    ai_summary = generate_ai_summary(
        overall_score,
        display_matched_skills,
        display_missing_skills
    )   
    

    return {
        "match_score": overall_score,
        "keyword_score": match_score,
        "semantic_score": semantic_score,
        "match_label": match_label,
        "matched_skills": display_matched_skills[:10],
        "missing_skills": display_missing_skills[:10],
        "match_explanation": match_explanation,
        "matched_groups": matched_groups,
        "ai_summary": ai_summary,
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyzer')
def analyzer():
    return render_template('analyze.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = request.form.get('resume_text', '')
    job_text = request.form.get('job_text', '')

    uploaded_file = request.files.get('resume_file')
    resume_name = "Pasted Resume"

    # if a file is uploaded then we use it instead of text
    if uploaded_file:
        filename = uploaded_file.filename.lower()
        resume_name = uploaded_file.filename

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
        suggestions=["Add more resume and job description text before analyzing."],
        ai_summary="Not enough information was provided to generate an AI hiring summary."
    )

    results = analyze_match(resume_text, job_text)
    save_analysis_result(resume_name, results)


    return render_template(
        'results.html',
        match_score=results["match_score"],
        keyword_score=results["keyword_score"],
        semantic_score=results["semantic_score"],
        match_label=results["match_label"],
        matched_skills=results["matched_skills"],
        missing_skills=results["missing_skills"],
        match_explanation=results["match_explanation"],
        ai_summary=results["ai_summary"],
    )

@app.route('/history')
def history():
    history_results = get_analysis_history()
    return render_template('history.html', history_results=history_results)

@app.route('/export')
def export_csv():

    history = get_analysis_history()

    filename = "fitcheck_results.csv"

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Resume",
            "Match Score",
            "Keyword Score",
            "Semantic Score",
            "Match Label",
            "Date"
        ])

        for row in history:
            writer.writerow(row)

    return send_file(
        filename,
        as_attachment=True
    )


def get_analysis_history():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT resume_name, match_score, keyword_score, semantic_score, match_label, created_at
        FROM analysis_results
        ORDER BY id DESC
    """)

    results = cursor.fetchall()

    conn.close()

    return results


if __name__ == '__main__':
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )