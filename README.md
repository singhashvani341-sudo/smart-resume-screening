# AI-Based Smart Resume Screening System

An AI-based application that screens, evaluates, and ranks multiple candidate resumes against a job description.

The system extracts candidate information from PDF and DOCX resumes, identifies skills, education, experience, and certifications, calculates multiple matching scores, ranks candidates, stores screening history, and provides dashboard filtering and CSV export.

## Core Features

- PDF and DOCX resume processing
- Multiple resume batch screening
- Candidate name, email, phone, and experience extraction
- Skill extraction and comparison
- Education detection
- Dynamic certification extraction
- Job description similarity scoring
- Weighted candidate scoring
- Automatic candidate ranking
- Corrupted resume failure isolation
- Repeated resume screening
- Persistent candidate history
- Candidate search and score filtering
- Sorting controls
- Complete and filtered CSV export
- Candidate history deletion
- Streamlit web interface
- Automated test suite

## Technology Stack

- Python 3.13
- Streamlit
- Pandas
- PyMuPDF
- python-docx
- scikit-learn
- SQLite
- Pytest

## Project Structure

```text
smart_resume_screening/
├── app.py
├── requirements.txt
├── pytest.ini
├── README.md
├── .gitignore
├── data/
├── database/
├── logs/
├── modules/
└── tests/

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart_resume_screening
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Windows:

```powershell
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in the default web browser.

## Usage

1. Enter the complete job description.
2. Set the required experience, education, and preferred certifications if applicable.
3. Upload one or more PDF or DOCX resumes.
4. Click `Screen and Rank Candidates`.
5. Review candidate rankings, scores, matched skills, missing skills, education, experience, and certifications.
6. Use Candidate History to search, filter, and sort previous screening records.
7. Export complete history or filtered results as CSV.

## Scoring System

The final candidate score is calculated using:

| Component | Weight |
| --- | ---: |
| Job Description Similarity | 30% |
| Skill Match | 30% |
| Experience Match | 20% |
| Education Match | 10% |
| Certification Match | 10% |

If an optional requirement is not specified, that component receives a score of 100.

## Running Tests

Run the complete test suite:

```bash
pytest -v
```

Current verified test result:

```text
136 passed
```
## Current Limitations

- Resume extraction quality depends on the structure and readability of the uploaded document.
- Image-only or scanned resumes are not supported without OCR.
- Candidate name extraction may be less accurate for unusual resume layouts.
- Dynamic certification extraction depends on identifiable certification section headings.
- Skill detection depends on the configured skills database.
- Screening results support recruitment decisions but should not replace human review.

## Future Improvements

- OCR support for scanned resumes
- Semantic skill detection using transformer models
- Advanced certification normalization
- Job-specific scoring configuration
- Candidate comparison charts
- Authentication and multiple user accounts
- Cloud database support
- Deployment for public access

## License

This project was developed for academic and educational purposes.