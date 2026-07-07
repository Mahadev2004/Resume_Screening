Resume Screening & Candidate Ranking System

Sorting through hundreds of resumes manually is incredibly time-consuming. I built this system to handle the heavy lifting of the initial screening process.

Under the hood, it extracts text from incoming resumes, compares them against a specific job description, and calculates a ranked shortlist. It includes a FastAPI backend, a custom scoring algorithm, and a clean web dashboard for recruiters to use.

What it actually does

Reads messy data: It handles standard PDFs and Word docs (using PyMuPDF and python-docx), but also falls back on EasyOCR to read scanned image-based resumes.

Smart semantic matching: It doesn't just do basic Ctrl+F keyword matching. It uses sentence-transformers and FAISS to actually understand the context and similarity of the applicant's experience to the job requirements.

Custom scoring formula: Candidates are ranked using a weighted system (40% skills match, 30% semantic similarity, 20% experience depth, 10% education).

Recruiter-friendly UI: Comes with a built-in dark-mode dashboard (styled with TailwindCSS) so non-technical users can upload files and view results without touching the API.

Useful extras: It automatically generates targeted interview questions based on a candidate's missing skills, and lets you dump the final shortlist straight into an Excel file.

How the pieces fit together

Data Flow

graph TD
    A[Web Dashboard] -->|Upload Resumes| B(FastAPI Backend)
    B --> C{File Type?}
    C -->|PDF/DOCX| D[Standard Text Parser]
    C -->|Scanned Image| E[EasyOCR]
    D --> F[spaCy NER & Extraction]
    E --> F
    F --> G[(PostgreSQL)]
    F --> H[SentenceTransformer]
    H --> I[(FAISS Vector Index)]
    I --> J[Weighted Ranking Engine]
    J --> K[Interview Question Generator]
    K --> A


Database Schema (Simplified)

erDiagram
    JOB_DESCRIPTION ||--o{ CANDIDATE_MATCH : "has"
    CANDIDATE ||--o{ CANDIDATE_MATCH : "has"
    
    JOB_DESCRIPTION {
        int id PK
        string title
        text raw_text
        array required_skills
        float min_experience_years
    }
    CANDIDATE {
        int id PK
        string full_name
        string email
        text raw_resume_text
        array extracted_skills
        float experience_years
    }
    CANDIDATE_MATCH {
        int id PK
        float total_score
        float skill_match_score
        float semantic_score
        json interview_questions
    }


Getting it running locally

The easy way (Docker)

If you have Docker Desktop installed, you can spin up the database and the API in one go:

Run docker-compose up --build

Open your browser to http://localhost:8000/ to see the dashboard.

If not installed and looking for the right version then install from postgreSQL and choose v1.17.10 which is pretty stable version among the latest releases.

The manual way (Local Python environment)

If you prefer running things natively without Docker, just make sure you have Python 3.11+ and a local PostgreSQL instance running.

Set up your virtual environment:

Use Python v3.11.9 as its is the most stable version available with most compatibility with stable libraries for working. So just write : python3.11 -m venv venv,  if you have more python versions installed on your device.

python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate


Install the required packages:

pip install -r requirements.txt


Download the NLP dictionary for spaCy (this is required for extracting names and skills):

python -m spacy download en_core_web_sm


Start the Uvicorn server:

uvicorn app.main:app --reload


Head over to http://localhost:8000/ for the UI, or http://localhost:8000/docs if you want to test the raw API endpoints directly via Swagger.