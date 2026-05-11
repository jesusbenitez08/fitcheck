# FitCheck

FitCheck is a web-based application that compares a user’s resume against a job description and provides a match score along with matched skills, missing skills, and actionable suggestions.

The goal of the project is to help job seekers better understand how closely their resume aligns with a role before applying, using both keyword analysis and natural language processing techniques.

---

## Beta Features (Current Development Stage)

FitCheck is now in Beta development, with core functionality implemented and ongoing improvements focused on usability, accuracy, and feature expansion.

Current features include:

* Resume text input through a web interface
* Job description text input
* Resume-to-job match scoring
* Match quality labels (Strong Match, Moderate Match, Low Match)
* NLP-based keyword extraction using spaCy
* Identification of matched and missing skills
* Dynamic suggestions based on missing keywords
* Improved keyword filtering using stop-word removal
* Enhanced UI with visual feedback (color indicators and skill badges)
* Input validation for better user experience

---

## Features in Progress (This Month)

To prepare FitCheck for user testing in Software Integration, the following features are currently being developed:

* Resume file upload support (PDF/DOCX)
* Improved scoring logic using NLP techniques
* Better keyword extraction and filtering accuracy
* Expanded suggestion system with more meaningful feedback
* Further UI/UX improvements for clarity and usability
* Initial semantic similarity comparison using embeddings

---

## Technologies

FitCheck is built using the following technologies:

* Python
* Flask (backend framework)
* HTML, CSS, and Jinja2 templating
* spaCy (natural language processing)
* Git and GitHub (version control)
* Jira (task tracking and workflow management)

Planned technologies:

* Sentence Transformers (semantic similarity)
* SQLite (lightweight database for persistence)

---

## Installation

To run FitCheck locally:

1. Clone the repository:

```bash
git clone https://github.com/jesusbenitez08/fitcheck.git
cd fitcheck
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

On Linux / WSL:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Run the application:

```bash
python app.py
```

6. Open in your browser:

```
http://127.0.0.1:5000/
```

---

## Development Setup

Key details for developers:

* Backend is built with Flask (`app.py`)
* NLP processing uses spaCy (`en_core_web_sm`)
* Templates are located in the `templates/` folder
* Static files (CSS) are located in the `static/` folder
* Virtual environment must be activated before running the app

Project structure:

```text
fitcheck/
├── app.py
├── README.md
├── requirements.txt
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   └── style.css
```

---

## Project Status

FitCheck is currently in **Beta development**.

The application is functional and ready for controlled testing, with ongoing improvements focused on accuracy, usability, and additional features.

---

## Known Issues

* Scoring is still primarily keyword-based
* Semantic similarity is not fully implemented yet
* File upload is not yet supported
* NLP extraction can still include some irrelevant terms

---

## Roadmap

Upcoming improvements include:

* Resume file upload (PDF/DOCX parsing)
* Advanced NLP scoring improvements
* Semantic similarity using embeddings
* More advanced suggestion system
* UI refinements and user experience improvements
* Database integration (SQLite)
* Preparation for user testing and feedback collection

---

## License

This project is licensed under the MIT License.

---

## Contributors

Jesus Benitez — Project owner, backend development, planning, and documentation
