import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class NotificationManager:
    @staticmethod
    def send_shortlist_email(candidate_email: str, candidate_name: str, job_title: str) -> bool:
        """
        Simulates an SMTP email dispatch to a shortlisted candidate.
        """
        # In a real production system, integrate SendGrid, AWS SES, or SMTPlib here.
        email_body = f"""
        Subject: Interview Invitation: {job_title} at Our Company
        
        Dear {candidate_name},
        
        We were highly impressed by your background and how well your skills align with our requirements for the {job_title} position.
        
        Our recruitment team would like to invite you for a preliminary interview...
        """
        logger.info(f"EMAIL DISPATCHED TO: {candidate_email}\nBODY:\n{email_body}")
        return True

class InterviewQuestionGenerator:
    @staticmethod
    def generate_questions(missing_skills: List[str], matched_skills: List[str]) -> List[str]:
        """
        Generates targeted interview questions based on the candidate's skill gap analysis.
        """
        questions = []
        
        # 1. Question based on strongest match
        if matched_skills:
            core_skill = matched_skills[0]
            questions.append(
                f"You have extensive experience with {core_skill.title()}. Can you walk me through the most complex project you built using it?"
            )
            
        # 2. Question probing the missing skills (Skill Gap)
        if missing_skills:
            gap_skill = missing_skills[0]
            questions.append(
                f"This role heavily utilizes {gap_skill.title()}, which wasn't prominent on your resume. How do you approach learning a new technology quickly, and have you encountered similar concepts before?"
            )
            
        # 3. Standard behavioral
        questions.append("Describe a time you had to optimize a slow-performing system or resolve a critical production bug under pressure.")
        
        return questions