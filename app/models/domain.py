from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ARRAY, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    raw_text = Column(Text, nullable=False)
    required_skills = Column(ARRAY(String), default=[])
    preferred_skills = Column(ARRAY(String), default=[])
    min_experience_years = Column(Float, default=0.0)
    required_education = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidates = relationship("CandidateMatch", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50), nullable=True)
    raw_resume_text = Column(Text, nullable=False)
    extracted_skills = Column(ARRAY(String), default=[])
    experience_years = Column(Float, default=0.0)
    education_level = Column(String(100), nullable=True)
    file_path = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    matches = relationship("CandidateMatch", back_populates="candidate")

class CandidateMatch(Base):
    __tablename__ = "candidate_matches"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"))
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    
    total_score = Column(Float, nullable=False)
    skill_match_score = Column(Float, nullable=False)
    semantic_similarity_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    
    matched_skills = Column(ARRAY(String), default=[])
    missing_skills = Column(ARRAY(String), default=[])
    preferred_skills_found = Column(ARRAY(String), default=[])
    interview_questions = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobDescription", back_populates="candidates")
    candidate = relationship("Candidate", back_populates="matches")