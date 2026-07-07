from typing import Dict, Any, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RankingEngine:
    @staticmethod
    def calculate_suitability(
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        candidate_embedding: np.ndarray,
        job_embedding: np.ndarray
    ) -> Dict[str, Any]:
        
        # 1. Skill Match (40% Weight)
        req_skills = set(job_data.get("required_skills", []))
        pref_skills = set(job_data.get("preferred_skills", []))
        cand_skills = set(candidate_data.get("skills", []))
        
        if req_skills:
            matched_req = req_skills.intersection(cand_skills)
            skill_score = (len(matched_req) / len(req_skills)) * 100.0
        else:
            skill_score = 100.0
            matched_req = set()
            
        missing_skills = list(req_skills - cand_skills)
        matched_pref = list(pref_skills.intersection(cand_skills))
        
        # Bonus vector for preferred skills
        if pref_skills and matched_pref:
            skill_score = min(100.0, skill_score + (len(matched_pref) / len(pref_skills)) * 15.0)

        # 2. Semantic Similarity Match (30% Weight)
        sim_matrix = cosine_similarity(candidate_embedding.reshape(1, -1), job_embedding.reshape(1, -1))
        semantic_score = max(0.0, float(sim_matrix[0][0])) * 100.0

        # 3. Experience Match (20% Weight)
        req_exp = job_data.get("min_experience_years", 0.0)
        cand_exp = candidate_data.get("experience_years", 0.0)
        if req_exp <= 0:
            exp_score = 100.0
        else:
            exp_score = min(100.0, (cand_exp / req_exp) * 100.0)

        # 4. Education Match (10% Weight)
        edu_score = 100.0 if candidate_data.get("education_level") != "Not Specified" else 50.0

        # Final Weighted Formula Calculation
        # Final Score = 40% Skill + 30% Semantic + 20% Exp + 10% Edu
        final_score = (
            0.40 * skill_score +
            0.30 * semantic_score +
            0.20 * exp_score +
            0.10 * edu_score
        )

        return {
            "candidate_name": candidate_data["name"],
            "score": round(final_score, 2),
            "breakdown": {
                "skill_match": round(skill_score, 2),
                "semantic_match": round(semantic_score, 2),
                "experience_match": round(exp_score, 2),
                "education_match": round(edu_score, 2)
            },
            "matched_skills": list(matched_req),
            "missing_skills": missing_skills,
            "preferred_skills": matched_pref
        }