from flask import Flask, render_template, request
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "we",
    "with", "you", "your", "our", "will", "this", "they", "their",
    "someone", "looking"
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
            keywords.add(token.lemma_)

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

    return {
        "match_score": match_score,
        "matched_skills": sorted(list(common_words))[:10],
        "missing_skills": sorted(list(missing_words))[:10]
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
        matched_skills=results["matched_skills"],
        missing_skills=results["missing_skills"]
    )

if __name__ == '__main__':
    app.run(debug=True)