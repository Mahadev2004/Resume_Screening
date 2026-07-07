import re
import io
import fitz
import docx
import spacy
from typing import Dict, Any, List
from app.ocr.engine import OCREngine

nlp = spacy.load("en_core_web_sm")
ocr_engine = OCREngine()

COMMON_SKILLS = {
    "python", "java", "c++", "fastapi", "django", "flask", "docker", "kubernetes",
    "aws", "gcp", "azure", "sql", "postgresql", "mongodb", "react", "node.js",
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow", "scikit-learn",
    "faiss", "git", "ci/cd", "linux", "rest api", "graphql"
}

class ResumeParser:
    @staticmethod
    def parse_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text = ""
        if filename.endswith(".pdf"):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text()
            if len(text.strip()) < 50: # Trigger OCR if PDF layer is image-only
                text = ocr_engine.extract_text_from_scanned_pdf(file_bytes)
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
        
        return ResumeParser.extract_metadata(text)

    @staticmethod
    def extract_metadata(text: str) -> Dict[str, Any]:
        doc = nlp(text)
        
        # Email & Phone extraction
        email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phone = re.findall(r'(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
        
        # Name heuristics (First PERSON entity found by spaCy)
        name = "Unknown Candidate"
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                name = ent.text.strip()
                break
                
        # Skills extraction via vocabulary matching
        text_lower = text.lower()
        extracted_skills = [skill for skill in COMMON_SKILLS if skill in text_lower]
        
        # Experience duration estimation via regex matches
        exp_years = 0.0
        exp_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?experience', text_lower)
        if exp_matches:
            exp_years = float(max(map(int, exp_matches)))
            
        return {
            "name": name,
            "email": email[0] if email else f"unknown_{hash(text)}@domain.com",
            "phone": phone[0] if phone else "N/A",
            "skills": extracted_skills,
            "experience_years": exp_years,
            "education_level": "Bachelor's" if "bachelor" in text_lower or "b.tech" in text_lower or "bs" in text_lower else "Master's" if "master" in text_lower or "ms" in text_lower else "Not Specified",
            "raw_text": text
        }