# AI-Powered Resume Analyzer

First phase backend for uploading resumes, extracting text from PDF files, identifying skills, and extracting education and experience details.

## Tech Stack

- Python
- FastAPI
- spaCy
- pdfplumber
- NLTK
- SQLite

## Folder Structure

```text
resume anaylzer/
├── app/
│   ├── core/
│   ├── controllers/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   └── utils/
├── data/
├── uploads/
│   └── resumes/
├── requirements.txt
└── README.md
```

## Installation

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Start the API server.

```bash
uvicorn app.main:app --reload
```

## API Documentation

### POST /upload-resume

Upload a single PDF resume.

Request:

```bash
curl -X POST "http://127.0.0.1:8000/upload-resume" \
  -F "file=@/path/to/resume.pdf"
```

Response:

```json
{
  "message": "Resume uploaded and processed successfully.",
  "resume_id": 1,
  "filename": "resume.pdf",
  "extracted_text": "...",
  "extracted_skills": ["Python", "SQL"]
}
```

### GET /resume-skills

Return stored resume skill extractions.

Optional query parameter:

- `resume_id`: Filter by a specific resume record.

Response:

```json
{
  "resumes": [
    {
      "resume_id": 1,
      "filename": "resume.pdf",
      "extracted_text": "...",
      "extracted_skills": ["Python", "SQL"],
      "created_at": "2026-06-23T12:00:00"
    }
  ]
}
```

## Notes

- Only PDF files are accepted.
- Files are validated for extension, MIME type, and size.
- Uploaded resumes are saved locally in `uploads/resumes/`.
- Skills are seeded into SQLite on first startup.
- Education and experience JSON is stored alongside each resume record for direct retrieval.

### GET /education

Return parsed education entries for a resume.

### GET /experience

Return parsed experience entries for a resume.

### GET /resume-analysis

Return the combined structured analysis payload.

### POST /analyze-job

Analyze a pasted job description and compare its required skills with a resume.

Request:

```bash
curl -X POST "http://127.0.0.1:8000/analyze-job" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We need a Python developer with 3+ years of experience using FastAPI, SQL, Docker, AWS, and Git. Bachelor'\''s degree in Computer Science preferred.",
    "resume_id": 1
  }'
```

If `resume_id` is omitted, the latest uploaded resume is used.

Response:

```json
{
  "job_skills": ["Python", "SQL", "Docker", "AWS", "Git", "FastAPI"],
  "resume_skills": ["Python", "SQL", "Git"],
  "matched_skills": ["Python", "SQL", "Git"],
  "missing_skills": ["Docker", "AWS", "FastAPI"],
  "required_technologies": ["FastAPI"],
  "experience_requirements": ["3+ years of experience"],
  "education_requirements": ["Bachelor's degree in Computer Science preferred"]
}
```

### POST /match-resume

Return a resume-to-job match score, matching skills, missing skills, and recommendations.

Request:

```bash
curl -X POST "http://127.0.0.1:8000/match-resume" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We need a Python developer with 3+ years of experience using FastAPI, SQL, Docker, AWS, and Git.",
    "resume_id": 1
  }'
```

If `resume_id` is omitted, the latest uploaded resume is used.

Response:

```json
{
  "match_score": 50,
  "matched_skills": ["Python", "SQL", "Git"],
  "missing_skills": ["Docker", "AWS", "FastAPI"],
  "recommendations": ["Learn Docker, AWS and FastAPI."]
}
```

### POST /ml-match

Return both the rule-based skill match score and the machine-learning text similarity score.

Request:

```bash
curl -X POST "http://127.0.0.1:8000/ml-match" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We need a Python developer with machine learning, SQL, Docker, AWS, Git, React, Node.js, and FastAPI experience.",
    "resume_id": 1
  }'
```

Response:

```json
{
  "skill_match": 75,
  "ml_similarity": 83
}
```

Score meaning:

- `skill_match`: rule-based score from matched extracted job skills divided by total extracted job skills.
- `ml_similarity`: Scikit-learn TF-IDF cosine similarity between the full resume text and full job description text.

### POST /ats-score

Evaluate an uploaded resume for ATS readiness.

Request:

```bash
curl -X POST "http://127.0.0.1:8000/ats-score" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": 1
  }'
```

If `resume_id` is omitted, the latest uploaded resume is scored.

Response:

```json
{
  "resume_id": 1,
  "filename": "resume.pdf",
  "ats_score": 82,
  "sections": {
    "contact_information": {
      "score": 15,
      "max_score": 20,
      "status": "needs_improvement",
      "issues": ["Missing GitHub profile."]
    }
  },
  "missing_sections": [],
  "weak_content": ["Experience section should include measurable achievements."],
  "formatting_issues": [],
  "suggestions": [
    "Add GitHub profile.",
    "Add measurable achievements with numbers, percentages, or impact."
  ]
}
```
