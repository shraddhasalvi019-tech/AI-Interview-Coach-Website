# AI-Powered Intelligent Interview Coaching and Candidate Assessment System Using Cloud-Based Generative AI

> **Academic Final-Year Software Engineering Project & Production-Grade Platform**

---

## 📌 Problem Statement

Traditional interview preparation platforms rely on static, pre-recorded question banks or simple automated multiple-choice quizzes. These systems fail to simulate the adaptive, conversational, and technical depth of real senior industry technical recruiters. Candidates lack personalized feedback on their specific answer nuances, multi-dimensional scoring (correctness, technical understanding, communication), context-aware follow-up probing, and actionable skill-gap analysis.

---

## 🎯 Main Objectives

1. **Adaptive AI Mock Interviews**: Dynamically generate context-aware interview questions based on candidate profile, target job role, experience level, and preferred difficulty.
2. **Contextual Follow-Up Probing**: Intelligently detect incomplete or vague candidate answers and ask targeted follow-up questions in real-time.
3. **Multi-Dimensional Answer Evaluation**: Rate candidate answers from 0–10 across 5 dimensions: Correctness, Relevance, Completeness, Technical Understanding, and Communication.
4. **Weighted Scoring Engine**: Compute overall interview performance using a documented, configurable multi-dimensional weighted formula.
5. **AI Skill-Gap Identification**: Benchmark candidate skills against industry-standard requirements for target roles.
6. **Comprehensive 12-Section Assessment Reports**: Generate print-ready candidate evaluation reports with detailed strengths, technical gaps, study recommendations, and exemplary model answer comparisons.

---

## 🛠️ Technology Stack

- **Programming Language**: Python 3.12
- **Backend Framework**: FastAPI (Async REST APIs, Pydantic data validation, OAuth2 JWT bearer token authentication)
- **Database**: PostgreSQL (SQLAlchemy 2.0 ORM with parameter security & automatic SQLite fallback for local zero-setup execution)
- **Generative AI Provider**: Cloud-based Generative AI API (Google Gemini API via `google-genai` SDK with modular provider abstraction)
- **Frontend Stack**: Vanilla HTML5, CSS3, and modern ES6 JavaScript (No heavyweight frameworks like React/Angular/Vue)
- **Security**: Bcrypt password hashing, JWT bearer token security, CORS middleware, defensive prompt injection isolation
- **Testing & Tooling**: Pytest, Uvicorn, OpenAPI / Swagger documentation (`/docs`)

---

## 📐 System Architecture

```
Candidate Browser (HTML5 / CSS3 / ES6 JS)
          │
          ▼  REST API (JWT Bearer Auth)
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│                                                         │
│  ┌──────────────┐   ┌─────────────────┐   ┌──────────┐  │
│  │ Auth Router  │   │ Interview State │   │ Report   │  │
│  │ & Security   │   │ Engine          │   │ Generator│  │
│  └──────────────┘   └─────────────────┘   └──────────┘  │
│         │                    │                 │        │
└─────────┼────────────────────┼─────────────────┼────────┘
          │                    │                 │
          ▼                    ▼                 ▼
  SQLAlchemy ORM        Scoring Service   AI Service Layer (ai_service.py)
          │                    │                 │
          ▼                    │                 ▼
┌──────────────────┐           │       Google Gemini Cloud API
│ PostgreSQL DB    │           │       (google-genai / JSON Mode)
│ (SQLite Fallback)│           │
└──────────────────┘           ▼
                  Multi-Dimensional Weighted Formula
```

---

## 🗄️ Database Design (Normalized ER Schema)

The database schema is normalized up to 3NF:

- `users`: User account credentials and registration metadata.
- `candidate_profiles`: Candidate education, skills, programming languages, experience level, target role, and preferred interview settings.
- `interviews`: Interview session configurations, status (`configured`, `in_progress`, `completed`), timestamps, and overall weighted dimension scores.
- `interview_questions`: Dynamic primary and follow-up questions linked to categories and targeted skills.
- `candidate_answers`: Raw text candidate responses and submission timestamps.
- `answer_evaluations`: 5-dimensional numerical scores (0–10) + specific strengths and improvement suggestions.
- `interview_feedbacks`: Aggregate AI feedback, technical gaps, communication tips, and sample model answer improvements.
- `skill_assessments`: Target role skill benchmark benchmarking and gap recommendations.

---

## 🚀 Environment Setup & Installation

### 1. Prerequisites
- Python 3.12+
- PostgreSQL (Optional; if PostgreSQL daemon is offline, system automatically initializes local SQLite database)

### 2. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/ai-interview-coach.git
cd ai-interview-coach

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Environment Variables Configuration (`.env`)
Create a `.env` file in the root directory (refer to `.env.example`):

```env
# Application Settings
APP_NAME="AI-Powered Intelligent Interview Coaching System"
DEBUG=True
SECRET_KEY="interview_ai_super_secret_jwt_key_academic_project_2026"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# PostgreSQL Connection (Primary)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/interview_ai_db
FALLBACK_SQLITE_URL=sqlite:///./interview_ai.db

# Cloud Generative AI Settings (Google Gemini API)
GENAI_PROVIDER=google
GENAI_API_KEY=YOUR_GEMINI_API_KEY_HERE
GENAI_MODEL=gemini-2.5-flash

# Multi-Dimensional Scoring Weights
WEIGHT_TECHNICAL=0.30
WEIGHT_CORRECTNESS=0.20
WEIGHT_COMPLETENESS=0.15
WEIGHT_RELEVANCE=0.15
WEIGHT_COMMUNICATION=0.20
```

---

## 🏃 Running the Application

### Launch Server
Run the single startup launcher:
```bash
python run.py
```
Or run directly via Uvicorn:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Access Points
- **Web Frontend Interface**: `http://127.0.0.1:8000/app/index.html`
- **Interactive Swagger OpenAPI Docs**: `http://127.0.0.1:8000/docs`
- **Health Check Endpoint**: `http://127.0.0.1:8000/api/health`

---

## 🧪 Automated Testing

Execute the automated test suite covering Auth, Profile, Interview Engine, AI Prompts parsing, and Scoring formulas:

```bash
python -m pytest tests/
```

Expected Output:
```
======================= 7 passed in 4.08s =======================
```

---

## ⚡ Quick Demo & Viva Presentation Workflow

1. Open `http://127.0.0.1:8000/app/index.html` in your browser.
2. Click **"🚀 Quick Demo Seed"** on the home page.
3. Login using pre-seeded credentials:
   - **Email**: `demo@example.com`
   - **Password**: `password123`
4. Explore the pre-computed **Candidate Dashboard**, **AI Skill-Gap Analysis**, and **Detailed 12-Section Report**.
5. Click **"+ Start Mock Interview"** to experience real-time AI question generation, answer evaluation, and follow-up checks.
