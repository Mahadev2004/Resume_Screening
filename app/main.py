from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import gc
from contextlib import asynccontextmanager

from app.database.session import engine, Base, get_db
from app.models.domain import JobDescription, Candidate, CandidateMatch
from app.services.parser import ResumeParser
from app.ranking.engine import RankingEngine
from sentence_transformers import SentenceTransformer

# --- Bonus Feature Imports ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from app.utils.export import ExportService
from app.notifications.manager import InterviewQuestionGenerator, NotificationManager
from app.embeddings.faiss_index import FaissSearchEngine

# Global model variables
embedder = None
faiss_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages startup and shutdown events to keep memory usage 
    stable during Render deployment.
    """
    global embedder, faiss_engine
    # Load heavy models only after the web server starts
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    faiss_engine = FaissSearchEngine()
    gc.collect()
    yield
    # Cleanup on shutdown
    embedder = None
    faiss_engine = None

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Resume Screening & Candidate Ranking System",
    description="Enterprise API with lazy-loaded AI models.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/api/v1/jobs", status_code=201)
def create_job_description(
    title: str = Form(...),
    raw_text: str = Form(...),
    required_skills: str = Form("python,fastapi,sql"),
    preferred_skills: str = Form("docker,aws"),
    min_experience_years: float = Form(2.0),
    db: Session = Depends(get_db)
):
    job = JobDescription(
        title=title,
        raw_text=raw_text,
        required_skills=[s.strip().lower() for s in required_skills.split(",")],
        preferred_skills=[s.strip().lower() for s in preferred_skills.split(",")],
        min_experience_years=min_experience_years
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"status": "success", "job_id": job.id, "title": job.title}

@app.post("/api/v1/resumes/screen/{job_id}")
async def screen_resumes(
    job_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    global embedder, faiss_engine
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job Description not found")
        
    job_embedding = embedder.encode(job.raw_text)
    results = []

    for file in files:
        contents = await file.read()
        parsed_meta = ResumeParser.parse_file(contents, file.filename)
        cand_embedding = embedder.encode(parsed_meta["raw_text"])
        
        candidate = Candidate(
            full_name=parsed_meta["name"],
            email=parsed_meta["email"],
            phone=parsed_meta["phone"],
            raw_resume_text=parsed_meta["raw_text"],
            extracted_skills=parsed_meta["skills"],
            experience_years=parsed_meta["experience_years"],
            education_level=parsed_meta["education_level"],
            file_path=f"/app/uploads/{file.filename}"
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        job_data = {
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "min_experience_years": job.min_experience_years
        }
        eval_result = RankingEngine.calculate_suitability(
            parsed_meta, job_data, cand_embedding, job_embedding
        )
        
        faiss_engine.add_vector(candidate.id, cand_embedding)
        
        interview_qs = InterviewQuestionGenerator.generate_questions(
            eval_result["missing_skills"], 
            eval_result["matched_skills"]
        )
        eval_result["interview_questions"] = interview_qs

        match = CandidateMatch(
            job_id=job.id,
            candidate_id=candidate.id,
            total_score=eval_result["score"],
            skill_match_score=eval_result["breakdown"]["skill_match"],
            semantic_similarity_score=eval_result["breakdown"]["semantic_match"],
            experience_score=eval_result["breakdown"]["experience_match"],
            education_score=eval_result["breakdown"]["education_match"],
            matched_skills=eval_result["matched_skills"],
            missing_skills=eval_result["missing_skills"],
            preferred_skills_found=eval_result["preferred_skills"],
            interview_questions=interview_qs
        )
        db.add(match)
        db.commit()

        results.append(eval_result)

    results.sort(key=lambda x: x["score"], reverse=True)
    
    if results and results[0]["score"] >= 80.0:
        NotificationManager.send_shortlist_email(
            candidate_email=results[0].get("email", "candidate@domain.com"),
            candidate_name=results[0]["candidate_name"],
            job_title=job.title
        )
        
    return {"job_id": job.id, "shortlisted_candidates": results}

@app.post("/api/v1/export/excel")
async def export_to_excel(data: dict):
    candidates = data.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates provided for export")
        
    excel_bytes = ExportService.export_candidates_to_excel(candidates)
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=shortlist_report.xlsx"}
    )

os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("frontend/index.html")
