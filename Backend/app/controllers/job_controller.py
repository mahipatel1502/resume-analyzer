from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.job import JobAnalysisRequest, JobAnalysisResponse, MLMatchResponse, ResumeJobMatchResponse
from app.services.job_analysis_service import JobAnalysisService


router = APIRouter(tags=["Jobs"], dependencies=[Depends(get_current_user)])
job_analysis_service = JobAnalysisService()


@router.post("/analyze-job", response_model=JobAnalysisResponse)
def analyze_job(request: JobAnalysisRequest) -> JobAnalysisResponse:
    return job_analysis_service.analyze_job(request)


@router.post("/match-resume", response_model=ResumeJobMatchResponse)
def match_resume(request: JobAnalysisRequest) -> ResumeJobMatchResponse:
    return job_analysis_service.match_resume(request)


@router.post("/ml-match", response_model=MLMatchResponse)
def ml_match(request: JobAnalysisRequest) -> MLMatchResponse:
    return job_analysis_service.ml_match(request)
