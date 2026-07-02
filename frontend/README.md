# Resume Analyzer — Frontend

A React + Tailwind CSS frontend for an AI-powered resume analyzer. Connects
to a FastAPI backend to upload a resume, submit a job description, and
display an ATS score, job-match score, skill gaps, and recommendations.

## Tech Stack

- **React 19** (Vite)
- **Tailwind CSS v4**
- **Axios** for API calls
- **React Router v7** for routing
- **Recharts** for the score breakdown bar chart and skills donut chart
- **lucide-react** for icons

## Getting Started

```bash
npm install
cp .env.example .env   # set VITE_API_BASE_URL to your FastAPI server
npm run dev
```

The app runs at `http://localhost:5173` by default.

To build for production:

```bash
npm run build
npm run preview   # serve the production build locally
```

## Project Structure

```
src/
  api/
    client.js          # Axios instance, error normalization, auth header
    endpoints.js        # One function per FastAPI endpoint
  components/           # Reusable UI: Card, ProgressBar, RadialGauge, etc.
  context/
    AnalysisContext.jsx  # Shared state: resume, job description, results
  pages/
    Home.jsx
    ResumeUpload.jsx
    JobDescription.jsx
    ResultsDashboard.jsx
    NotFound.jsx
  App.jsx
  main.jsx
  index.css             # Tailwind v4 theme tokens (design system)
```

## Pages

1. **Home** — product overview, sample readout, entry point into the flow.
2. **Resume Upload** — drag-and-drop or click-to-browse upload with progress
   bar and validation (PDF/DOC/DOCX, 10MB max).
3. **Job Description** — form for job title, company, and full description
   text; submits and immediately triggers analysis.
4. **Results Dashboard** — ATS score and match score as radial gauges, a
   score breakdown chart, a skills-coverage donut, skills-found / missing
   tag lists, and a prioritized recommendations list.

## FastAPI Endpoint Contract

Update `src/api/endpoints.js` if your backend's route names or payload
shapes differ. The frontend currently expects:

| Method | Path                      | Purpose                                   |
|--------|---------------------------|--------------------------------------------|
| POST   | `/resume/upload`          | Multipart upload, returns `{ resume_id, filename, parsed_skills }` |
| POST   | `/resume/parse`           | `{ resume_id }` → structured resume fields |
| POST   | `/job-description/submit` | `{ resume_id, job_title, company, description_text }` → `{ jd_id }` |
| POST   | `/analyze`                | `{ resume_id, jd_id }` → `AnalysisResult` (below) |
| GET    | `/analyze/{analysis_id}`  | Fetch a previously computed result        |
| GET    | `/resume/history`         | List past uploads/analyses                 |
| DELETE | `/resume/{resume_id}`     | Remove an uploaded resume                  |
| GET    | `/health`                 | Backend health check                       |

**`AnalysisResult` shape** (drives the entire Results Dashboard):

```json
{
  "analysis_id": "string",
  "ats_score": 82,
  "match_score": 67,
  "skills_found": ["Python", "FastAPI", "Docker"],
  "missing_skills": ["Kubernetes"],
  "recommendations": [
    "Add a project that uses container orchestration to close the Kubernetes gap.",
    "Quantify the impact of your CNN-based deepfake detection project with a metric."
  ],
  "score_breakdown": {
    "formatting": 90,
    "keyword_match": 70,
    "experience_relevance": 60,
    "education_match": 85
  },
  "resume_filename": "resume.pdf",
  "job_title": "Machine Learning Engineer"
}
```

`score_breakdown` is optional — if your backend doesn't return it, that
chart card is simply omitted from the dashboard.

### CORS

Make sure your FastAPI app allows the frontend's origin, e.g.:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Design System

The visual language is an "instrument panel" theme: a deep navy-ink
background (`--color-ink-950` etc.) with a single signal-lime accent
(`--color-signal-500`) used for primary scores and actions, plus cyan,
amber, and rose accents for secondary states. Headings use Space Grotesk,
body text uses Inter, and data/labels use JetBrains Mono. All tokens live
in `src/index.css` under the `@theme` block (Tailwind v4's CSS-based
config) — change them there to retheme the whole app.

The signature component is `RadialGauge` (`src/components/RadialGauge.jsx`),
an animated dial readout used for the ATS and Match scores.
