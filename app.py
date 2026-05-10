from flask import Flask, render_template, request
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "we",
    "with", "you", "your", "our", "will", "this", "they", "their",
    "someone", "looking", "data", "skill", "skills", "role", "candidate",
    "experience", "work", "job", "description", "looking", "required", 
    "requirement", "requirements"
}

def extract_keywords(text: str):
    doc = nlp(text.lower())
    keywords = set()

    for token in doc:
        if (
            token.is_alpha
            and not token.is_stop
            and token.text not in STOP_WORDS
            and len(token.text) > 2
            and token.pos_ in {"NOUN", "PROPN", "ADJ"}
        ):
            keyword = token.lemma_.strip()
            if keyword not in STOP_WORDS and len(keyword) > 2:
                keywords.add(keyword)

    return keywords

def analyze_match(resume_text: str, job_text: str):
    resume_words = extract_keywords(resume_text)
    job_words = extract_keywords(job_text)

    common_words = resume_words.intersection(job_words)
    missing_words = job_words.difference(resume_words)

    if len(job_words) == 0:
        match_score = 0
    else:
        match_score = int((len(common_words) / len(job_words)) * 100)

    if match_score >= 70:
        match_label = "Strong Match"
        match_explanation = "This resume is a strong match because most of the important keywords from the job description were found."
    elif match_score >= 40:
        match_label = "Moderate Match"
        match_explanation = "This resume has some overlap with the job description, but there are still important skills missing."
    else:
        match_label = "Low Match"
        match_explanation = "This resume has limited overlap with the job description and may need more targeted skills or experience."

    suggestions = [
        f"Add experience related to {word} to improve your match."
        for word in sorted(list(missing_words))[:5]
    ]

    return {
        "match_score": match_score,
        "match_label": match_label,
        "matched_skills": sorted(list(common_words))[:10],
        "missing_skills": sorted(list(missing_words))[:10],
        "match_explanation": match_explanation,
        "suggestions": suggestions
    }

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = request.form.get('resume_text', '')
    job_text = request.form.get('job_text', '')

    results = analyze_match(resume_text, job_text)

    return render_template(
        'results.html',
        match_score=results["match_score"],
        match_label=results["match_label"],
        matched_skills=results["matched_skills"],
        missing_skills=results["missing_skills"],
        suggestions=results["suggestions"],
        match_explanation=results["match_explanation"],
    )

if __name__ == '__main__':
    app.run(debug=True)