from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.ats_controller import router as ats_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.frontend_controller import router as frontend_router
from app.controllers.job_controller import router as job_router
from app.controllers.resume_controller import router as resume_router
from app.database.database import initialize_database


app = FastAPI(
    title="AI-Powered Resume Analyzer",
    version="1.0.0",
    description="Upload resumes, extract text from PDF files, and identify predefined skills.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    initialize_database()


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {"message": "Resume Analyzer API is running."}


app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(ats_router)
app.include_router(frontend_router)
