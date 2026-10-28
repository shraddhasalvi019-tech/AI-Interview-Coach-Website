FEEDBACK_PROMPT = """You are a senior hiring manager and executive interview coach creating a comprehensive candidate assessment report.

CANDIDATE PROFILE:
- Name: {candidate_name}
- Target Role: {target_role}
- Experience Level: {experience_level}

INTERVIEW PERFORMANCE DATA:
- Total Questions Conducted: {total_questions}
- Overall Score: {overall_score}%
- Technical Score: {technical_score}%
- Communication Score: {communication_score}%
- Relevance Score: {relevance_score}%
- Correctness Score: {correctness_score}%
- Completeness Score: {completeness_score}%

FULL QUESTION & ANSWER EVALUATION TRANSCRIPT:
{transcript}

TASK:
Synthesize the overall performance into a detailed, actionable, personalized candidate assessment report.

REQUIRED JSON OUTPUT FORMAT:
```json
{{
    "overall_summary": "Detailed summary of candidate performance across technical and interpersonal dimensions...",
    "strengths": [
        "Strong foundation in core data structures and OOP concepts",
        "Clear and structured verbal communication flow"
    ],
    "weaknesses": [
        "Struggled to articulate concurrency control and thread safety mechanics",
        "Omitted time/space complexity analysis in algorithmic answers"
    ],
    "technical_gaps": [
        "Java Concurrency & Multithreading (ReentrantLock, ExecutorService)",
        "RESTful API HTTP status codes and error handling best practices"
    ],
    "communication_issues": [
        "Tended to give abstract definitions before giving concrete examples",
        "Could adopt the STAR (Situation, Task, Action, Result) method for behavioral scenarios"
    ],
    "recommended_topics": [
        "Java Collections Framework (HashMap vs ConcurrentHashMap)",
        "Multithreading & Synchronization",
        "Database Indexing & Query Optimization"
    ],
    "practice_areas": [
        "Mock coding interviews focusing on system design & data structures",
        "Behavioral interview preparation using structured storytelling"
    ],
    "tips": [
        "Always state algorithmic complexity (Big-O) proactively when explaining technical solutions",
        "Use concrete code snippets or pseudocode to ground abstract explanations"
    ],
    "sample_answer_improvements": [
        {{
            "question": "Sample question text",
            "candidate_answer": "Sample raw candidate answer",
            "improved_answer": "An exemplary, candidate-tailored response demonstrating ideal depth, structure, and clarity."
        }}
    ]
}}
```
"""
