-- PostgreSQL Database Schema for Resume Screening System

-- Table: job_descriptions
CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    raw_text TEXT NOT NULL,
    required_skills TEXT[] DEFAULT '{}',
    preferred_skills TEXT[] DEFAULT '{}',
    min_experience_years FLOAT DEFAULT 0.0,
    required_education VARCHAR(100),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: candidates
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    raw_resume_text TEXT NOT NULL,
    extracted_skills TEXT[] DEFAULT '{}',
    experience_years FLOAT DEFAULT 0.0,
    education_level VARCHAR(100),
    file_path VARCHAR(512) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_candidates_email ON candidates(email);

-- Table: candidate_matches
CREATE TABLE candidate_matches (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    
    total_score FLOAT NOT NULL,
    skill_match_score FLOAT NOT NULL,
    semantic_similarity_score FLOAT NOT NULL,
    experience_score FLOAT NOT NULL,
    education_score FLOAT NOT NULL,
    
    matched_skills TEXT[] DEFAULT '{}',
    missing_skills TEXT[] DEFAULT '{}',
    preferred_skills_found TEXT[] DEFAULT '{}',
    interview_questions JSON DEFAULT '[]',
    
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);