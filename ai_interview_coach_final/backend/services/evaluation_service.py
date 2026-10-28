from typing import List, Dict, Any
from backend.config import settings
from backend.models.evaluation import AnswerEvaluation

class EvaluationService:
    def __init__(self):
        self.w_tech = settings.WEIGHT_TECHNICAL
        self.w_corr = settings.WEIGHT_CORRECTNESS
        self.w_comp = settings.WEIGHT_COMPLETENESS
        self.w_relev = settings.WEIGHT_RELEVANCE
        self.w_comm = settings.WEIGHT_COMMUNICATION

    def calculate_question_score(
        self,
        correctness: float,
        relevance: float,
        completeness: float,
        technical_understanding: float,
        communication: float
    ) -> float:
        """
        Calculates a single question's weighted overall score (0.0 - 10.0 scale)
        Formula:
        0.30 * Technical + 0.20 * Correctness + 0.15 * Completeness + 0.15 * Relevance + 0.20 * Communication
        """
        score = (
            (self.w_tech * technical_understanding) +
            (self.w_corr * correctness) +
            (self.w_comp * completeness) +
            (self.w_relev * relevance) +
            (self.w_comm * communication)
        )
        return round(score, 2)

    def calculate_interview_scores(self, evaluations: List[AnswerEvaluation]) -> Dict[str, float]:
        """
        Calculates aggregate interview dimension percentages (0.0% to 100.0%)
        across all evaluated questions in a completed interview session.
        """
        if not evaluations:
            return {
                "overall_score": 0.0,
                "technical_score": 0.0,
                "communication_score": 0.0,
                "relevance_score": 0.0,
                "correctness_score": 0.0,
                "completeness_score": 0.0
            }

        count = len(evaluations)
        avg_tech = sum(e.technical_understanding for e in evaluations) / count
        avg_corr = sum(e.correctness for e in evaluations) / count
        avg_comp = sum(e.completeness for e in evaluations) / count
        avg_relev = sum(e.relevance for e in evaluations) / count
        avg_comm = sum(e.communication for e in evaluations) / count

        # Overall weighted score out of 10.0
        weighted_avg = (
            (self.w_tech * avg_tech) +
            (self.w_corr * avg_corr) +
            (self.w_comp * avg_comp) +
            (self.w_relev * avg_relev) +
            (self.w_comm * avg_comm)
        )

        # Convert 0-10 ratings to 0-100% percentages
        return {
            "overall_score": round(weighted_avg * 10.0, 1),
            "technical_score": round(avg_tech * 10.0, 1),
            "communication_score": round(avg_comm * 10.0, 1),
            "relevance_score": round(avg_relev * 10.0, 1),
            "correctness_score": round(avg_corr * 10.0, 1),
            "completeness_score": round(avg_comp * 10.0, 1)
        }

evaluation_service = EvaluationService()
