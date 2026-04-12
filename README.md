# FitCheck

FitCheck is a web based application that compares a user’s resume against a job description and provides a match score along with matched and missing keywords. The goal of the project is to help job seekers better understand how closely their resume aligns with a role before applying.

This project is useful because many applicants submit resumes without knowing whether they match the skills and requirements listed in a job posting. FitCheck is being developed to make that process clearer and more approachable through resume analysis and, later, natural language processing features.

## Alpha Features

By the end of this month, FitCheck will include:

- Resume text input through a web interface
- Job description text input
- Resume-to-job match scoring
- Identification of matched keywords between resume and job description
- Identification of missing keywords from the job description
- Improved keyword filtering using stop-word removal

AI-focused features (in progress):

- NLP-based skill extraction using spaCy
- Semantic similarity analysis between resume and job description using embeddings
- More intelligent scoring beyond simple keyword matching

## Technologies

FitCheck is being built using the following technologies:

- Python
- Flask (backend framework)
- HTML and basic templating (Jinja2)
- Git and GitHub for version control
- Jira for task tracking and workflow management

Planned technologies and libraries:

- spaCy for natural language processing and skill extraction
- Sentence Transformers for semantic similarity analysis between resume and job description
- SQLite for lightweight data storage


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

6. Open the app in your browser:

   http://127.0.0.1:5000/


## Development Setup

Key details for developers:

- The project uses Flask for the backend  
- The main entry point is `app.py`  
- HTML templates are stored in the `templates/` folder  
- A virtual environment must be activated before running the app  
- Current functionality includes resume input, job description input, and basic keyword matching  

Project structure:

```text
fitcheck/
├── app.py
├── README.md
├── requirements.txt
├── templates/
│   ├── index.html
│   └── results.html
```
To start development:

1. Clone the repo
2. Create and activate a virtual environment
3. Install dependencies
4. Run python app.py
5. Open the browser

## License

This project is licensed under the MIT License.

## Contributors

Jesus Benitez — Project owner, backend development, planning, and documentation

## Project Status

FitCheck is currently in early Alpha development.

Current features include:

- Working Flask application
- Resume and job description input
- Basic keyword match scoring
- Matched and missing keyword results
- Stop-word filtering for cleaner results

AI features are planned for the next phase.

## Known Issues

- Matching is still keyword-based and not fully intelligent
- No file upload support yet
- UI is very basic
- NLP features are not implemented yet

## Roadmap

Planned improvements:

- Add resume file upload (PDF/DOCX)
- Improve scoring using NLP techniques
- Implement skill extraction with spaCy
- Add semantic similarity scoring (embeddings)
- Improve UI to match design prototype
- Integrate SQLite for data storage
- Expand feedback with actionable suggestions