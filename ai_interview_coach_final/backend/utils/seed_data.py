from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.profile import CandidateProfile
from backend.models.interview import Interview
from backend.models.question import InterviewQuestion
from backend.models.answer import CandidateAnswer
from backend.models.evaluation import AnswerEvaluation
from backend.models.feedback import InterviewFeedback
from backend.utils.security import get_password_hash

def seed_demo_candidate_data(db: Session):
    """Seeds the database with a pre-built demo candidate and sample interview assessment."""
    email = "demo@example.com"
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            name="Demo Candidate",
            password_hash=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        profile = CandidateProfile(
            user_id=user.id,
            full_name="Demo Candidate",
            education="B.Tech in Computer Science & Engineering",
            skills=["Java", "SQL", "HTML", "CSS", "Python"],
            programming_languages=["Java", "Python"],
            experience_level="Fresher",
            target_role="Java Developer",
            preferred_interview_type="Technical",
            preferred_difficulty="Medium"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Check if demo interview exists
    existing_interview = db.query(Interview).filter(Interview.user_id == user.id).first()
    if existing_interview:
        return {"message": "Demo data already seeded.", "user_email": email, "password": "password123", "interview_id": existing_interview.id}

    # Create completed demo interview
    interview = Interview(
        user_id=user.id,
        target_role="Java Developer",
        interview_type="Technical",
        difficulty="Medium",
        total_questions=3,
        status="completed",
        overall_score=82.0,
        technical_score=85.0,
        communication_score=78.0,
        relevance_score=86.0,
        correctness_score=84.0,
        completeness_score=76.0,
        completed_at=datetime.utcnow()
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # Question 1 & Answer
    q1 = InterviewQuestion(
        interview_id=interview.id,
        question_order=1,
        question_text="Explain the internal working of HashMap in Java and how hash collisions are handled.",
        category="Technical",
        targeted_skill="Java Collections",
        difficulty="Medium",
        is_follow_up=False
    )
    db.add(q1)
    db.commit()
    db.refresh(q1)

    a1 = CandidateAnswer(
        interview_id=interview.id,
        question_id=q1.id,
        answer_text="HashMap in Java works on the principle of hashing. It uses an internal array of Node buckets. When put(key, value) is called, it computes key.hashCode() and determines bucket index using (n - 1) & hash. If two keys produce the same index, a hash collision occurs, which is handled using a LinkedList at that bucket. In Java 8+, if bucket size exceeds 8, it converts to a Balanced Tree (Red-Black Tree) for O(log N) performance."
    )
    db.add(a1)
    db.commit()
    db.refresh(a1)

    e1 = AnswerEvaluation(
        answer_id=a1.id,
        correctness=9.0,
        relevance=9.5,
        completeness=8.5,
        technical_understanding=9.0,
        communication=8.5,
        overall_score=8.9,
        strengths=["Accurately explained bucket indexing and hashing equation", "Correctly cited Java 8 Red-Black Tree optimization"],
        improvements=["Mention load factor (0.75 default) and rehashing capacity doubling"],
        feedback_text="Exemplary response showing clear mastery of Java Collections internals."
    )
    db.add(e1)

    # Question 2 & Answer
    q2 = InterviewQuestion(
        interview_id=interview.id,
        question_order=2,
        question_text="What is the difference between single inheritance and multilevel inheritance in Java?",
        category="Technical",
        targeted_skill="OOP Principles",
        difficulty="Easy",
        is_follow_up=False
    )
    db.add(q2)
    db.commit()
    db.refresh(q2)

    a2 = CandidateAnswer(
        interview_id=interview.id,
        question_id=q2.id,
        answer_text="Single inheritance means one subclass inherits directly from one superclass. Multilevel inheritance means a class inherits from a derived class, forming a chain like Class C extends Class B, and Class B extends Class A. Java does not support multiple inheritance with classes to avoid the diamond problem, but supports it via interfaces."
    )
    db.add(a2)
    db.commit()
    db.refresh(a2)

    e2 = AnswerEvaluation(
        answer_id=a2.id,
        correctness=8.5,
        relevance=8.5,
        completeness=8.0,
        technical_understanding=8.5,
        communication=8.0,
        overall_score=8.3,
        strengths=["Clear explanation of inheritance hierarchy", "Proactively mentioned avoidance of Diamond Problem"],
        improvements=["Provide a small code snippet demonstrating 'extends' keyword"],
        feedback_text="Very good answer with clear conceptual distinction."
    )
    db.add(e2)

    # Feedback
    fb = InterviewFeedback(
        interview_id=interview.id,
        overall_summary="Demo Candidate demonstrated strong proficiency in core Java concepts, object-oriented design, and data structures. Technical score reached 85% with articulate technical communication.",
        strengths=["Deep understanding of Java HashMap internals & JVM memory optimizations", "Proactive mention of edge cases and Diamond problem in OOP"],
        weaknesses=["Could state space/time complexity explicitly for algorithm questions", "Provide brief code snippets to illustrate structural concepts"],
        technical_gaps=["Java Concurrency & Thread Synchronization", "Spring Boot REST Controller Annotations"],
        communication_issues=["Ensure responses always follow a structured format: Definition -> Code Example -> Complexity"],
        recommended_topics=["Java Collections Framework", "Multithreading & ReentrantLock", "Spring Boot REST API Development"],
        practice_areas=["System Design Mock Interviews", "SQL Joins & Indexing"],
        tips=["State Big-O complexity upfront", "Discuss edge cases during technical answers"],
        sample_answer_improvements=[
            {
                "question": "What is the difference between ArrayList and LinkedList in Java?",
                "candidate_answer": "ArrayList uses arrays and LinkedList uses nodes.",
                "improved_answer": "ArrayList uses a contiguous dynamic array offering O(1) random access by index but O(N) insertion/deletion in the middle. LinkedList uses a doubly-linked node list offering O(1) insertion/deletion at pointers but O(N) sequential search."
            }
        ]
    )
    db.add(fb)
    db.commit()

    return {
        "message": "Demo candidate and sample interview seeded successfully!",
        "user_email": email,
        "password": "password123",
        "interview_id": interview.id
    }
