from uuid import uuid4

from fastapi import HTTPException, status

from app.models.analysis import (
    AnalysisHistoryResponse,
    AnalysisResult,
    AnalyzeRequest,
    JobDescriptionSubmitRequest,
    JobDescriptionSubmitResponse,
    ResumeParseRequest,
    ResumeParseResponse,
    ScoreBreakdown,
)
from app.models.ats import ATSScoreRequest
from app.models.job import JobAnalysisRequest
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.ats_score_service import ATSScoreService
from app.services.job_analysis_service import JobAnalysisService


class AnalysisOrchestrationService:
    def __init__(self) -> None:
        self.analysis_repository = AnalysisRepository()
        self.resume_repository = ResumeRepository()
        self.ats_score_service = ATSScoreService()
        self.job_analysis_service = JobAnalysisService()

    def submit_job_description(self, request: JobDescriptionSubmitRequest) -> JobDescriptionSubmitResponse:
        resume_payload = self.resume_repository.get_resume_payload(request.resume_id)
        if resume_payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

        jd_id = self.analysis_repository.save_job_description(
            resume_id=request.resume_id,
            job_title=request.job_title.strip(),
            company=request.company.strip(),
            description_text=request.description_text,
        )
        return JobDescriptionSubmitResponse(jd_id=jd_id)

    def run_analysis(self, request: AnalyzeRequest) -> AnalysisResult:
        resume_payload = self.resume_repository.get_resume_payload(request.resume_id)
        if resume_payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

        job_description = self.analysis_repository.get_job_description(request.jd_id)
        if job_description is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")

        if int(job_description["resume_id"]) != request.resume_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description does not belong to the selected resume.",
            )

        job_request = JobAnalysisRequest(
            job_description=str(job_description["description_text"]),
            resume_id=request.resume_id,
        )
        ats_result = self.ats_score_service.score_resume(ATSScoreRequest(resume_id=request.resume_id))
        match_result = self.job_analysis_service.match_resume(job_request)
        ml_result = self.job_analysis_service.ml_match(job_request)
        job_analysis = self.job_analysis_service.analyze_job(job_request)

        result = self._compose_analysis_result(
            analysis_id=uuid4().hex,
            resume_id=request.resume_id,
            jd_id=request.jd_id,
            resume_filename=str(resume_payload["filename"]),
            job_title=str(job_description.get("job_title", "")),
            company=str(job_description.get("company", "")),
            ats_result=ats_result,
            match_result=match_result,
            ml_result=ml_result,
            job_analysis=job_analysis,
        )
        self.analysis_repository.save_analysis(
            analysis_id=result.analysis_id,
            resume_id=request.resume_id,
            jd_id=request.jd_id,
            result=result.model_dump(),
        )
        return result

    def get_analysis(self, analysis_id: str) -> AnalysisResult:
        stored_result = self.analysis_repository.get_analysis(analysis_id)
        if stored_result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
        return AnalysisResult(**stored_result)

    def get_history(self) -> AnalysisHistoryResponse:
        return AnalysisHistoryResponse(items=self.analysis_repository.list_analyses())

    def parse_resume(self, request: ResumeParseRequest) -> ResumeParseResponse:
        resume_payload = self.resume_repository.get_resume_payload(request.resume_id)
        if resume_payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

        return ResumeParseResponse(
            resume_id=int(resume_payload["resume_id"]),
            filename=str(resume_payload["filename"]),
            skills=[str(skill) for skill in resume_payload.get("extracted_skills", [])],
            education=resume_payload.get("education", []),
            experience=resume_payload.get("experience", []),
            raw_text=str(resume_payload.get("extracted_text", "")),
        )

    def _compose_analysis_result(
        self,
        analysis_id: str,
        resume_id: int,
        jd_id: int,
        resume_filename: str,
        job_title: str,
        company: str,
        ats_result,
        match_result,
        ml_result,
        job_analysis,
    ) -> AnalysisResult:
        sections = ats_result.sections
        score_breakdown = ScoreBreakdown(
            formatting=self._section_percentage(sections["formatting"]),
            keyword_match=match_result.match_score,
            ml_similarity=ml_result.ml_similarity,
            experience_relevance=self._section_percentage(sections["experience"]),
            education_match=self._section_percentage(sections["education"]),
        )
        recommendations = self._merge_recommendations(match_result.recommendations, ats_result.suggestions)

        return AnalysisResult(
            analysis_id=analysis_id,
            resume_id=resume_id,
            jd_id=jd_id,
            ats_score=ats_result.ats_score,
            match_score=match_result.match_score,
            ml_score=ml_result.ml_similarity,
            skills_found=match_result.matched_skills,
            missing_skills=match_result.missing_skills,
            recommendations=recommendations,
            score_breakdown=score_breakdown,
            resume_filename=resume_filename,
            job_title=job_title,
            company=company,
            job_analysis=job_analysis,
            ats_details=ats_result,
            match_details=match_result,
            ml_details=ml_result,
        )

    def _section_percentage(self, section) -> int:
        if section.max_score <= 0:
            return 0
        return round((section.score / section.max_score) * 100)

    def _merge_recommendations(self, match_recommendations: list[str], ats_suggestions: list[str]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for recommendation in [*match_recommendations, *ats_suggestions]:
            normalized = recommendation.strip()
            if not normalized:
                continue
            key = normalized.casefold()
            if key in seen:
                continue
            seen.add(key)
            merged.append(normalized)
        return merged
