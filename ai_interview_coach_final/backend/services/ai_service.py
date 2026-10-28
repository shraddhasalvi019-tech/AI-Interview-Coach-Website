import time
import logging
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.utils.validators import parse_llm_json, clamp_score
from backend.prompts import (
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    FOLLOW_UP_PROMPT,
    FEEDBACK_PROMPT,
    SKILL_GAP_PROMPT
)

logger = logging.getLogger("interview_ai.ai_service")

# Models tried (in order) after the one configured in .env
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]
MAX_ATTEMPTS = 4          # per model, for temporary overload errors (503/429)
BACKOFF_SECONDS = [2, 4, 8]


class AIServiceError(Exception):
    """Raised when the Gemini API cannot produce a usable response."""


class AIService:
    def __init__(self):
        self.api_key = (settings.GENAI_API_KEY or "").strip().strip('"').strip("'")
        self.model_name = settings.GENAI_MODEL
        self.clients: List[tuple] = []          # (mode_name, genai.Client)
        self.models: List[str] = []
        self._working: Optional[tuple] = None   # (client_index, model) that last succeeded
        self.last_error: Optional[str] = None

        self.models = [self.model_name] + [m for m in FALLBACK_MODELS if m != self.model_name]

        if not self.api_key:
            logger.error("GENAI_API_KEY is empty - set it in the .env file.")
            return

        try:
            from google import genai
        except Exception as e:
            self.last_error = f"google-genai SDK not installed: {e}"
            logger.error(self.last_error)
            return

        # Standard Gemini Developer API keys start with 'AIza'. Other formats
        # (e.g. 'AQ.') are Vertex AI express-mode keys, so we try that mode first for them.
        # Developer API is tried first (it accepts this key); Vertex mode is only a last resort.
        order = ["developer", "vertex"]

        for mode in order:
            try:
                if mode == "developer":
                    self.clients.append((mode, genai.Client(api_key=self.api_key)))
                else:
                    self.clients.append((mode, genai.Client(vertexai=True, api_key=self.api_key)))
            except Exception as e:
                logger.warning(f"Could not create '{mode}' GenAI client: {e}")

        if self.clients:
            logger.info(f"GenAI ready. Modes={[m for m, _ in self.clients]} models={self.models}")

    def _call_llm(self, prompt: str) -> str:
        """Calls Gemini and returns the raw text. Raises AIServiceError on failure (no hardcoded fallback)."""
        if not self.api_key:
            raise AIServiceError("GENAI_API_KEY is not set. Add your Gemini API key to the .env file and restart the server.")
        if not self.clients:
            raise AIServiceError(f"Gemini client could not be initialised. {self.last_error or 'Check google-genai installation.'}")

        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        )

        combos = [(i, m) for i in range(len(self.clients)) for m in self.models]
        if self._working in combos:
            combos.remove(self._working)
            combos.insert(0, self._working)

        key_accepted = False  # True once Google answers with anything other than an auth error
        for idx, model in combos:
            mode, client = self.clients[idx]
            # Vertex mode is only worth trying if the developer API rejected the key itself
            if mode == "vertex" and key_accepted:
                continue
            for attempt in range(MAX_ATTEMPTS):
                try:
                    response = client.models.generate_content(model=model, contents=prompt, config=config)
                    text = getattr(response, "text", None)
                    if text and text.strip():
                        self._working = (idx, model)
                        self.last_error = None
                        return text
                    self.last_error = f"[{mode}/{model}] empty response"
                    break
                except Exception as e:
                    msg = str(e)
                    self.last_error = f"[{mode}/{model}] {msg[:300]}"
                    logger.warning(f"Gemini call failed: {self.last_error}")
                    transient = any(t in msg for t in ("429", "503", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "timed out", "Timeout"))
                    if mode == "developer" and any(t in msg for t in ("404", "NOT_FOUND", "503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED")):
                        key_accepted = True
                    if transient and attempt < MAX_ATTEMPTS - 1:
                        time.sleep(BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)])
                        continue
                    break  # permanent error for this combo -> try next one

        raise AIServiceError(f"Gemini API request failed. Last error: {self.last_error}")

    def _generate_json(self, prompt: str, required_key: str) -> Dict[str, Any]:
        """Calls Gemini and returns validated JSON containing required_key (retries once on bad JSON)."""
        last = None
        for _ in range(2):
            raw = self._call_llm(prompt)
            try:
                data = parse_llm_json(raw)
                if isinstance(data, list) and data:
                    data = data[0]
                if isinstance(data, dict) and required_key in data:
                    return data
                last = f"missing field '{required_key}'"
            except Exception as e:
                last = str(e)
            logger.warning(f"Invalid AI response ({last}); retrying...")
        raise AIServiceError(f"Gemini returned an invalid response ({last}). Please try again.")

    def generate_question(
        self,
        candidate_name: str,
        target_role: str,
        experience_level: str,
        skills: List[str],
        programming_languages: List[str],
        interview_type: str,
        difficulty: str,
        question_order: int,
        total_questions: int,
        previous_questions: List[str]
    ) -> Dict[str, Any]:
        """Generates a dynamic interview question tailored to the candidate profile."""
        prompt = QUESTION_GENERATION_PROMPT.format(
            candidate_name=candidate_name,
            target_role=target_role,
            experience_level=experience_level,
            skills=", ".join(skills) if skills else "General CS",
            programming_languages=", ".join(programming_languages) if programming_languages else "General",
            interview_type=interview_type,
            difficulty=difficulty,
            question_order=question_order,
            total_questions=total_questions,
            previous_questions=", ".join(previous_questions) if previous_questions else "None"
        )

        data = None
        for _ in range(2):  # re-ask once if the model repeats an earlier question
            data = self._generate_json(prompt, "question")
            if str(data["question"]).strip().lower() not in [q.strip().lower() for q in previous_questions]:
                break
        return {
            "question": str(data["question"]).strip(),
            "category": data.get("category", interview_type),
            "targeted_skill": data.get("targeted_skill", skills[0] if skills else "General"),
            "difficulty": data.get("difficulty", difficulty)
        }

    def evaluate_answer(
        self,
        target_role: str,
        experience_level: str,
        question_text: str,
        category: str,
        targeted_skill: str,
        difficulty: str,
        candidate_answer: str
    ) -> Dict[str, Any]:
        """Evaluates candidate's answer across 5 scoring dimensions."""
        prompt = ANSWER_EVALUATION_PROMPT.format(
            target_role=target_role,
            experience_level=experience_level,
            question_text=question_text,
            category=category,
            targeted_skill=targeted_skill or "General",
            difficulty=difficulty,
            candidate_answer=candidate_answer
        )

        data = self._generate_json(prompt, "correctness")
        return {
            "correctness": clamp_score(data.get("correctness", 5.0)),
            "relevance": clamp_score(data.get("relevance", 5.0)),
            "completeness": clamp_score(data.get("completeness", 5.0)),
            "technical_understanding": clamp_score(data.get("technical_understanding", 5.0)),
            "communication": clamp_score(data.get("communication", 5.0)),
            "overall_score": clamp_score(data.get("overall_score", 5.0)),
            "strengths": data.get("strengths", []),
            "improvements": data.get("improvements", []),
            "feedback_text": data.get("feedback_text", ""),
            "needs_follow_up": bool(data.get("needs_follow_up", False)),
            "follow_up_question": data.get("follow_up_question") or None
        }

    def check_follow_up(
        self,
        question_text: str,
        candidate_answer: str,
        experience_level: str,
        target_role: str,
        correctness: float,
        completeness: float
    ) -> Dict[str, Any]:
        """Determines whether a follow-up question is necessary."""
        prompt = FOLLOW_UP_PROMPT.format(
            question_text=question_text,
            candidate_answer=candidate_answer,
            experience_level=experience_level,
            target_role=target_role,
            correctness=correctness,
            completeness=completeness
        )

        data = self._generate_json(prompt, "needs_follow_up")
        return {
            "needs_follow_up": bool(data.get("needs_follow_up", False)),
            "reason": data.get("reason", ""),
            "follow_up_question": data.get("follow_up_question", None)
        }

    def generate_feedback(
        self,
        candidate_name: str,
        target_role: str,
        experience_level: str,
        total_questions: int,
        overall_score: float,
        technical_score: float,
        communication_score: float,
        relevance_score: float,
        correctness_score: float,
        completeness_score: float,
        transcript: str
    ) -> Dict[str, Any]:
        """Generates comprehensive final assessment report and feedback."""
        prompt = FEEDBACK_PROMPT.format(
            candidate_name=candidate_name,
            target_role=target_role,
            experience_level=experience_level,
            total_questions=total_questions,
            overall_score=overall_score,
            technical_score=technical_score,
            communication_score=communication_score,
            relevance_score=relevance_score,
            correctness_score=correctness_score,
            completeness_score=completeness_score,
            transcript=transcript
        )

        return self._generate_json(prompt, "overall_summary")

    def analyze_skill_gap(
        self,
        target_role: str,
        experience_level: str,
        candidate_skills: List[str],
        programming_languages: List[str]
    ) -> Dict[str, Any]:
        """Performs AI skill-gap analysis comparing candidate skills against target role standard."""
        prompt = SKILL_GAP_PROMPT.format(
            target_role=target_role,
            experience_level=experience_level,
            candidate_skills=", ".join(candidate_skills) if candidate_skills else "None specified",
            programming_languages=", ".join(programming_languages) if programming_languages else "None specified"
        )

        try:
            return self._generate_json(prompt, "strong_skills")
        except AIServiceError as e:
            logger.warning(f"Skill-gap AI unavailable, using benchmark comparison: {e}")
            return self._fallback_skill_gap(target_role, candidate_skills)

    # Deterministic benchmark used only for the skill-gap page if Gemini is unreachable
    def _fallback_skill_gap(self, role: str, candidate_skills: List[str]) -> Dict[str, Any]:
        role_benchmarks = {
            "Java Developer": ["Java", "OOP", "Collections", "Exception Handling", "Multithreading", "SQL", "REST APIs", "Spring Boot"],
            "Python Developer": ["Python", "Data Structures", "OOP", "FastAPI", "Django", "SQL", "PostgreSQL", "REST APIs", "Git"],
            "Software Developer": ["Data Structures", "Algorithms", "OOP", "SQL", "Git", "REST APIs", "System Design", "Docker"],
            "Data Analyst": ["Python", "SQL", "Pandas", "NumPy", "Data Visualization", "Power BI", "Statistics", "Excel"],
            "Machine Learning Engineer": ["Python", "PyTorch", "Scikit-Learn", "SQL", "Data Pipelines", "MLOps", "Model Deployment", "Git"]
        }
        
        expected = role_benchmarks.get(role, role_benchmarks["Software Developer"])
        strong = [s for s in candidate_skills if s.lower() in [e.lower() for e in expected]]
        if not strong and candidate_skills:
            strong = candidate_skills[:2]
        
        to_improve = [e for e in expected if e.lower() not in [s.lower() for s in candidate_skills]]
        
        return {
            "target_role": role,
            "expected_skills": expected,
            "strong_skills": strong if strong else ["Programming Fundamentals"],
            "skills_to_improve": to_improve[:4] if to_improve else ["System Architecture"],
            "recommended_learning_areas": [f"{s} Fundamentals & Best Practices" for s in to_improve[:3]]
        }

ai_service = AIService()
