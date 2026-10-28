SKILL_GAP_PROMPT = """You are an AI career advisor and tech skill assessor comparing candidate skills against industry standards.

TARGET ROLE: {target_role}
EXPERIENCE LEVEL: {experience_level}
CANDIDATE DECLARED SKILLS: {candidate_skills}
CANDIDATE PROGRAMMING LANGUAGES: {programming_languages}

TASK:
Perform a skill-gap analysis. Identify skills the candidate possesses that strongly align with {target_role}, missing or weak skills expected by industry recruiters for a {experience_level} {target_role}, and specific recommended learning areas.

REQUIRED JSON OUTPUT FORMAT:
```json
{{
    "target_role": "{target_role}",
    "expected_skills": ["List", "of", "industry", "standard", "skills", "for", "this", "role"],
    "strong_skills": ["Matched", "strong", "candidate", "skills"],
    "skills_to_improve": ["Missing", "or", "weak", "skills", "requiring", "upskilling"],
    "recommended_learning_areas": ["Specific", "topics", "courses", "or", "frameworks", "to", "learn"]
}}
```
"""
