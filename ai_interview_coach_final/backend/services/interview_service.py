import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.interview import Interview
from backend.models.question import InterviewQuestion
from backend.models.answer import CandidateAnswer
from backend.models.evaluation import AnswerEvaluation
from backend.models.feedback import InterviewFeedback
from backend.models.profile import CandidateProfile
from backend.services.ai_service import ai_service
from backend.services.evaluation_service import evaluation_service

logger = logging.getLogger("interview_ai.interview_service")

class InterviewService:
    def create_interview(
        self,
        db: Session,
        user_id: int,
        target_role: Optional[str],
        interview_type: str,
        difficulty: str,
        total_questions: int
    ) -> Interview:
        """Creates a new mock interview session."""
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        role = target_role or (profile.target_role if profile else "Software Developer")

        interview = Interview(
            user_id=user_id,
            target_role=role,
            interview_type=interview_type,
            difficulty=difficulty,
            total_questions=total_questions,
            status="configured"
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)
        return interview

    def start_interview(self, db: Session, interview_id: int, user_id: int) -> InterviewQuestion:
        """Starts an interview session and generates the first dynamic question."""
        interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail="Interview session not found.")

        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        name = profile.full_name if profile else "Candidate"
        exp = profile.experience_level if profile else "Fresher"
        skills = profile.skills if profile else ["General CS"]
        langs = profile.programming_languages if profile else ["Python", "Java"]

        interview.status = "in_progress"
        db.commit()

        # Generate first question
        q_data = ai_service.generate_question(
            candidate_name=name,
            target_role=interview.target_role,
            experience_level=exp,
            skills=skills,
            programming_languages=langs,
            interview_type=interview.interview_type,
            difficulty=interview.difficulty,
            question_order=1,
            total_questions=interview.total_questions,
            previous_questions=[]
        )

        question = InterviewQuestion(
            interview_id=interview.id,
            question_order=1,
            question_text=q_data["question"],
            category=q_data.get("category", interview.interview_type),
            targeted_skill=q_data.get("targeted_skill"),
            difficulty=q_data.get("difficulty", interview.difficulty),
            is_follow_up=False
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question

    def submit_answer(
        self,
        db: Session,
        interview_id: int,
        user_id: int,
        question_id: int,
        answer_text: str
    ) -> Dict[str, Any]:
        """Submits candidate answer, triggers AI evaluation, and handles follow-up generation."""
        interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail="Interview session not found.")

        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == question_id,
            InterviewQuestion.interview_id == interview_id
        ).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found.")

        # Check if answer already exists
        existing_ans = db.query(CandidateAnswer).filter(CandidateAnswer.question_id == question_id).first()
        if existing_ans:
            answer = existing_ans
            answer.answer_text = answer_text
            answer.submitted_at = datetime.utcnow()
        else:
            answer = CandidateAnswer(
                interview_id=interview_id,
                question_id=question_id,
                answer_text=answer_text
            )
            db.add(answer)
            db.commit()
            db.refresh(answer)

        # Retrieve profile context
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        exp = profile.experience_level if profile else "Fresher"
        skills = profile.skills if profile else ["General CS"]
        langs = profile.programming_languages if profile else ["Java"]
        name = profile.full_name if profile else "Candidate"

        # Count progress & previous questions BEFORE calling AI so the next question
        # can be generated in parallel with the evaluation (cuts waiting time).
        answered_count = db.query(CandidateAnswer).filter(CandidateAnswer.interview_id == interview_id).count()
        prev_questions = [q.question_text for q in db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview_id).all()]
        may_need_next = answered_count < interview.total_questions

        def _eval():
            return ai_service.evaluate_answer(
                target_role=interview.target_role,
                experience_level=exp,
                question_text=question.question_text,
                category=question.category,
                targeted_skill=question.targeted_skill or "General",
                difficulty=question.difficulty,
                candidate_answer=answer_text
            )

        def _next():
            return ai_service.generate_question(
                candidate_name=name,
                target_role=interview.target_role,
                experience_level=exp,
                skills=skills,
                programming_languages=langs,
                interview_type=interview.interview_type,
                difficulty=interview.difficulty,
                question_order=answered_count + 1,
                total_questions=interview.total_questions,
                previous_questions=prev_questions
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            eval_future = pool.submit(_eval)
            next_future = pool.submit(_next) if may_need_next else None
            eval_data = eval_future.result()
            prefetched_next = None
            if next_future is not None:
                try:
                    prefetched_next = next_future.result()
                except Exception as e:
                    logger.warning(f"Prefetch of next question failed, will retry if needed: {e}")

        overall_eval_score = evaluation_service.calculate_question_score(
            correctness=eval_data["correctness"],
            relevance=eval_data["relevance"],
            completeness=eval_data["completeness"],
            technical_understanding=eval_data["technical_understanding"],
            communication=eval_data["communication"]
        )

        # Store evaluation
        existing_eval = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == answer.id).first()
        if existing_eval:
            evaluation = existing_eval
            evaluation.correctness = eval_data["correctness"]
            evaluation.relevance = eval_data["relevance"]
            evaluation.completeness = eval_data["completeness"]
            evaluation.technical_understanding = eval_data["technical_understanding"]
            evaluation.communication = eval_data["communication"]
            evaluation.overall_score = overall_eval_score
            evaluation.strengths = eval_data["strengths"]
            evaluation.improvements = eval_data["improvements"]
            evaluation.feedback_text = eval_data["feedback_text"]
        else:
            evaluation = AnswerEvaluation(
                answer_id=answer.id,
                correctness=eval_data["correctness"],
                relevance=eval_data["relevance"],
                completeness=eval_data["completeness"],
                technical_understanding=eval_data["technical_understanding"],
                communication=eval_data["communication"],
                overall_score=overall_eval_score,
                strengths=eval_data["strengths"],
                improvements=eval_data["improvements"],
                feedback_text=eval_data["feedback_text"]
            )
            db.add(evaluation)
        db.commit()

        # Follow-up check (only for primary non-follow-up questions)
        follow_up_q = None
        has_follow_up = False
        if not question.is_follow_up:
            fu_decision = {
                "needs_follow_up": eval_data.get("needs_follow_up", False),
                "follow_up_question": eval_data.get("follow_up_question")
            }
            if fu_decision.get("needs_follow_up") and fu_decision.get("follow_up_question"):
                has_follow_up = True
                follow_up_q = InterviewQuestion(
                    interview_id=interview_id,
                    question_order=question.question_order + 1,
                    question_text=fu_decision["follow_up_question"],
                    category=question.category,
                    targeted_skill=question.targeted_skill,
                    difficulty=question.difficulty,
                    is_follow_up=True,
                    parent_question_id=question.id
                )
                db.add(follow_up_q)
                db.commit()
                db.refresh(follow_up_q)

        # Determine next question or interview completion
        questions_count = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview_id).count()
        answered_count = db.query(CandidateAnswer).filter(CandidateAnswer.interview_id == interview_id).count()

        is_completed = answered_count >= interview.total_questions and not has_follow_up
        next_q = None

        if has_follow_up:
            next_q = follow_up_q
        elif not is_completed:
            # Use the question generated in parallel (or generate now if the prefetch failed)
            q_next_data = prefetched_next
            if q_next_data is None:
                q_next_data = _next()
            next_q = InterviewQuestion(
                interview_id=interview_id,
                question_order=answered_count + 1,
                question_text=q_next_data["question"],
                category=q_next_data.get("category", interview.interview_type),
                targeted_skill=q_next_data.get("targeted_skill"),
                difficulty=q_next_data.get("difficulty", interview.difficulty),
                is_follow_up=False
            )
            db.add(next_q)
            db.commit()
            db.refresh(next_q)

        if is_completed:
            self.complete_interview(db, interview_id, user_id)

        return {
            "answer_id": answer.id,
            "evaluation": eval_data,
            "has_follow_up": has_follow_up,
            "follow_up_question": follow_up_q,
            "is_interview_completed": is_completed,
            "next_question": next_q
        }

    def complete_interview(self, db: Session, interview_id: int, user_id: int) -> Interview:
        """Finalizes completed interview, calculates multi-dimensional scores, and generates AI feedback."""
        interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user_id).first()
        if not interview:
            raise HTTPException(status_code=404, detail="Interview session not found.")

        # Get all evaluations
        evaluations = db.query(AnswerEvaluation).join(CandidateAnswer).filter(CandidateAnswer.interview_id == interview_id).all()
        scores = evaluation_service.calculate_interview_scores(evaluations)

        interview.overall_score = scores["overall_score"]
        interview.technical_score = scores["technical_score"]
        interview.communication_score = scores["communication_score"]
        interview.relevance_score = scores["relevance_score"]
        interview.correctness_score = scores["correctness_score"]
        interview.completeness_score = scores["completeness_score"]
        interview.status = "completed"
        interview.completed_at = datetime.utcnow()
        db.commit()

        # Build transcript for GenAI Feedback Generation
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        name = profile.full_name if profile else "Candidate"
        exp = profile.experience_level if profile else "Fresher"

        qa_pairs = db.query(InterviewQuestion, CandidateAnswer).join(CandidateAnswer, CandidateAnswer.question_id == InterviewQuestion.id).filter(InterviewQuestion.interview_id == interview_id).all()
        transcript_lines = []
        for q, a in qa_pairs:
            transcript_lines.append(f"Q: {q.question_text}\nA: {a.answer_text}\n---")
        transcript_str = "\n".join(transcript_lines)

        fb_data = ai_service.generate_feedback(
            candidate_name=name,
            target_role=interview.target_role,
            experience_level=exp,
            total_questions=len(qa_pairs),
            overall_score=interview.overall_score,
            technical_score=interview.technical_score,
            communication_score=interview.communication_score,
            relevance_score=interview.relevance_score,
            correctness_score=interview.correctness_score,
            completeness_score=interview.completeness_score,
            transcript=transcript_str
        )

        existing_fb = db.query(InterviewFeedback).filter(InterviewFeedback.interview_id == interview_id).first()
        if existing_fb:
            feedback = existing_fb
            feedback.overall_summary = fb_data.get("overall_summary", "Interview completed.")
            feedback.strengths = fb_data.get("strengths", [])
            feedback.weaknesses = fb_data.get("weaknesses", [])
            feedback.technical_gaps = fb_data.get("technical_gaps", [])
            feedback.communication_issues = fb_data.get("communication_issues", [])
            feedback.recommended_topics = fb_data.get("recommended_topics", [])
            feedback.practice_areas = fb_data.get("practice_areas", [])
            feedback.tips = fb_data.get("tips", [])
            feedback.sample_answer_improvements = fb_data.get("sample_answer_improvements", [])
        else:
            feedback = InterviewFeedback(
                interview_id=interview_id,
                overall_summary=fb_data.get("overall_summary", "Interview completed successfully."),
                strengths=fb_data.get("strengths", []),
                weaknesses=fb_data.get("weaknesses", []),
                technical_gaps=fb_data.get("technical_gaps", []),
                communication_issues=fb_data.get("communication_issues", []),
                recommended_topics=fb_data.get("recommended_topics", []),
                practice_areas=fb_data.get("practice_areas", []),
                tips=fb_data.get("tips", []),
                sample_answer_improvements=fb_data.get("sample_answer_improvements", [])
            )
            db.add(feedback)
        db.commit()
        db.refresh(interview)
        return interview

interview_service = InterviewService()
