from typing import Dict, Any, List
from backend.services.ai_service import ai_service
from backend.models.profile import CandidateProfile

class SkillService:
    def get_skill_gap_analysis(self, profile: CandidateProfile) -> Dict[str, Any]:
        """
        Executes skill gap analysis comparing candidate declared skills
        against expected industry benchmarks for their target role.
        """
        target_role = profile.target_role or "Software Developer"
        experience_level = profile.experience_level or "Fresher"
        candidate_skills = profile.skills or []
        programming_languages = profile.programming_languages or []

        return ai_service.analyze_skill_gap(
            target_role=target_role,
            experience_level=experience_level,
            candidate_skills=candidate_skills,
            programming_languages=programming_languages
        )

skill_service = SkillService()
