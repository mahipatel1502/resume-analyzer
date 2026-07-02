from uuid import uuid4
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import ALLOWED_CONTENT_TYPE, MAX_UPLOAD_SIZE_BYTES, UPLOAD_DIR
from app.models.resume import EducationResponse, ExperienceResponse, ResumeAnalysisResponse, ResumeRecord, ResumeSkillsResponse, ResumeUploadResponse
from app.repositories.resume_repository import ResumeRepository
from app.services.pdf_service import PDFService
from app.services.resume_analysis_service import ResumeAnalysisService
from app.services.text_service import TextService


class ResumeService:
    def __init__(self) -> None:
        self.resume_repository = ResumeRepository()
        self.pdf_service = PDFService()
        self.text_service = TextService()
        self.analysis_service = ResumeAnalysisService()

    async def upload_resume(self, file: UploadFile) -> ResumeUploadResponse:
        self._validate_upload(file)
        original_filename = file.filename or "resume.pdf"
        stored_filename = f"{uuid4().hex}.pdf"
        file_path = UPLOAD_DIR / stored_filename

        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 5 MB limit.",
            )

        file_path.write_bytes(content)

        try:
            extracted_text = self.pdf_service.extract_text(file_path)
        except Exception as exc:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file could not be processed as a valid PDF.",
            ) from exc

        cleaned_text = self.text_service.clean_text(extracted_text)
        analysis = self.analysis_service.analyze(extracted_text)
        resume_id = self.resume_repository.save_resume(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            extracted_text=cleaned_text,
            extracted_skills=analysis["skills"],
            education_entries=analysis["education"],
            experience_entries=analysis["experience"],
        )

        return ResumeUploadResponse(
            message="Resume uploaded and processed successfully.",
            resume_id=resume_id,
            filename=original_filename,
            extracted_text=cleaned_text,
            analysis=ResumeAnalysisResponse(
                education=analysis["education"],
                experience=analysis["experience"],
                skills=analysis["skills"],
            ),
        )

    def get_resume_skills(self, resume_id: int | None = None) -> ResumeSkillsResponse:
        resume_rows = self.resume_repository.list_resumes(resume_id)
        records = [ResumeRecord(**row) for row in resume_rows]
        return ResumeSkillsResponse(resumes=records)

    def get_education(self, resume_id: int | None = None) -> EducationResponse:
        resume_payload = self._get_resume_payload(resume_id)
        return EducationResponse(
            resume_id=resume_payload["resume_id"],
            filename=resume_payload["filename"],
            education=resume_payload["education"],
        )

    def get_experience(self, resume_id: int | None = None) -> ExperienceResponse:
        resume_payload = self._get_resume_payload(resume_id)
        return ExperienceResponse(
            resume_id=resume_payload["resume_id"],
            filename=resume_payload["filename"],
            experience=resume_payload["experience"],
        )

    def get_resume_analysis(self, resume_id: int | None = None) -> ResumeAnalysisResponse:
        resume_payload = self._get_resume_payload(resume_id)
        return ResumeAnalysisResponse(
            education=resume_payload["education"],
            experience=resume_payload["experience"],
            skills=resume_payload["extracted_skills"],
        )

    def reanalyze_resume(self, resume_id: int | None = None) -> ResumeAnalysisResponse:
        file_record = self.resume_repository.get_resume_file_record(resume_id)
        if file_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found.",
            )

        resume_file_path = Path(str(file_record["file_path"]))
        if not resume_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stored resume file is missing. Re-upload the resume.",
            )

        extracted_text = self.pdf_service.extract_text(resume_file_path)
        analysis = self.analysis_service.analyze(extracted_text)
        self.resume_repository.update_resume_analysis(
            resume_id=int(file_record["resume_id"]),
            extracted_skills=analysis["skills"],
            education_entries=analysis["education"],
            experience_entries=analysis["experience"],
        )

        return ResumeAnalysisResponse(
            education=analysis["education"],
            experience=analysis["experience"],
            skills=analysis["skills"],
        )

    def _validate_upload(self, file: UploadFile) -> None:
        filename = file.filename or ""
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        if (file.content_type or "").lower() != ALLOWED_CONTENT_TYPE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Upload a valid PDF document.",
            )

    def _get_resume_payload(self, resume_id: int | None = None) -> dict[str, object]:
        resume_payload = self.resume_repository.get_resume_payload(resume_id)
        if resume_payload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume analysis not found.",
            )
        return resume_payload
