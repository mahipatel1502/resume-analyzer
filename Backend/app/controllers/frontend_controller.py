from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies.auth import get_current_user
from app.models.analysis import (
    AnalysisHistoryResponse,
    AnalysisResult,
    AnalyzeRequest,
    FrontendResumeUploadResponse,
    JobDescriptionSubmitRequest,
    JobDescriptionSubmitResponse,
    ResumeParseRequest,
    ResumeParseResponse,
)
from app.repositories.resume_repository import ResumeRepository
from app.services.analysis_orchestration_service import AnalysisOrchestrationService
from app.services.resume_service import ResumeService


router = APIRouter(tags=["Frontend API"], dependencies=[Depends(get_current_user)])
resume_service = ResumeService()
analysis_service = AnalysisOrchestrationService()
resume_repository = ResumeRepository()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Resume Analyzer API is running."}


@router.post("/resume/upload", response_model=FrontendResumeUploadResponse)
async def upload_resume_frontend(file: UploadFile = File(...)) -> FrontendResumeUploadResponse:
    result = await resume_service.upload_resume(file)
    return FrontendResumeUploadResponse(
        resume_id=result.resume_id,
        filename=result.filename,
        extracted_text=result.extracted_text,
        parsed_skills=result.analysis.skills,
    )


@router.post("/resume/parse", response_model=ResumeParseResponse)
def parse_resume_frontend(request: ResumeParseRequest) -> ResumeParseResponse:
    return analysis_service.parse_resume(request)


@router.post("/job-description/submit", response_model=JobDescriptionSubmitResponse)
def submit_job_description(request: JobDescriptionSubmitRequest) -> JobDescriptionSubmitResponse:
    return analysis_service.submit_job_description(request)


@router.post("/analyze", response_model=AnalysisResult)
def analyze_resume(request: AnalyzeRequest) -> AnalysisResult:
    return analysis_service.run_analysis(request)


@router.get("/analyze/{analysis_id}", response_model=AnalysisResult)
def get_analysis(analysis_id: str) -> AnalysisResult:
    return analysis_service.get_analysis(analysis_id)


@router.get("/resume/history", response_model=AnalysisHistoryResponse)
def get_analysis_history() -> AnalysisHistoryResponse:
    return analysis_service.get_history()


@router.delete("/resume/{resume_id}")
def delete_resume(resume_id: int) -> dict[str, str]:
    deleted = resume_repository.delete_resume(resume_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return {"message": "Resume deleted successfully."}
