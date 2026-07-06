from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies.auth import get_current_user
from app.models.resume import EducationResponse, ExperienceResponse, ResumeAnalysisResponse, ResumeSkillsResponse, ResumeUploadResponse
from app.services.resume_service import ResumeService


router = APIRouter(tags=["Resumes"], dependencies=[Depends(get_current_user)])
resume_service = ResumeService()


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), current_user: dict[str, object] = Depends(get_current_user)) -> ResumeUploadResponse:
    return await resume_service.upload_resume(file, int(current_user["id"]))


@router.get("/resume-skills", response_model=ResumeSkillsResponse)
def get_resume_skills(resume_id: int | None = None, current_user: dict[str, object] = Depends(get_current_user)) -> ResumeSkillsResponse:
    return resume_service.get_resume_skills(int(current_user["id"]), resume_id)


@router.get("/education", response_model=EducationResponse)
def get_education(resume_id: int | None = None, current_user: dict[str, object] = Depends(get_current_user)) -> EducationResponse:
    return resume_service.get_education(int(current_user["id"]), resume_id)


@router.get("/experience", response_model=ExperienceResponse)
def get_experience(resume_id: int | None = None, current_user: dict[str, object] = Depends(get_current_user)) -> ExperienceResponse:
    return resume_service.get_experience(int(current_user["id"]), resume_id)


@router.get("/resume-analysis", response_model=ResumeAnalysisResponse)
def get_resume_analysis(resume_id: int | None = None, current_user: dict[str, object] = Depends(get_current_user)) -> ResumeAnalysisResponse:
    return resume_service.get_resume_analysis(int(current_user["id"]), resume_id)


@router.post("/reanalyze-resume", response_model=ResumeAnalysisResponse)
def reanalyze_resume(resume_id: int | None = None, current_user: dict[str, object] = Depends(get_current_user)) -> ResumeAnalysisResponse:
    return resume_service.reanalyze_resume(int(current_user["id"]), resume_id)
