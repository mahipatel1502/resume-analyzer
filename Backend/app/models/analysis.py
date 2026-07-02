from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.ats import ATSScoreResponse
from app.models.job import JobAnalysisResponse, MLMatchResponse, ResumeJobMatchResponse


class JobDescriptionSubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resume_id: int = Field(gt=0)
    job_title: str = Field(default="", max_length=200)
    company: str = Field(default="", max_length=200)
    description_text: str = Field(..., min_length=30, max_length=20000)

    @field_validator("description_text")
    @classmethod
    def validate_description(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Job description cannot be empty.")
        if len(normalized_value.split()) < 5:
            raise ValueError("Job description is too short to analyze.")
        return normalized_value


class JobDescriptionSubmitResponse(BaseModel):
    jd_id: int


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resume_id: int = Field(gt=0)
    jd_id: int = Field(gt=0)


class ScoreBreakdown(BaseModel):
    formatting: int = Field(ge=0, le=100)
    keyword_match: int = Field(ge=0, le=100)
    ml_similarity: int = Field(default=0, ge=0, le=100)
    experience_relevance: int = Field(ge=0, le=100)
    education_match: int = Field(ge=0, le=100)


class AnalysisResult(BaseModel):
    analysis_id: str
    resume_id: int = 0
    jd_id: int = 0
    ats_score: int = Field(ge=0, le=100)
    match_score: int = Field(ge=0, le=100)
    ml_score: int = Field(default=0, ge=0, le=100)
    skills_found: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    score_breakdown: ScoreBreakdown
    resume_filename: str
    job_title: str
    company: str = ""
    job_analysis: JobAnalysisResponse | None = None
    ats_details: ATSScoreResponse | None = None
    match_details: ResumeJobMatchResponse | None = None
    ml_details: MLMatchResponse | None = None


class FrontendResumeUploadResponse(BaseModel):
    resume_id: int
    filename: str
    extracted_text: str
    parsed_skills: list[str] = Field(default_factory=list)


class ResumeParseRequest(BaseModel):
    resume_id: int = Field(gt=0)


class ResumeParseResponse(BaseModel):
    resume_id: int
    filename: str
    skills: list[str] = Field(default_factory=list)
    education: list[dict[str, object]] = Field(default_factory=list)
    experience: list[dict[str, object]] = Field(default_factory=list)
    raw_text: str = ""


class AnalysisHistoryItem(BaseModel):
    analysis_id: str
    resume_id: int
    jd_id: int
    resume_filename: str
    job_title: str
    company: str = ""
    ats_score: int
    match_score: int
    ml_score: int = 0
    created_at: str


class AnalysisHistoryResponse(BaseModel):
    items: list[AnalysisHistoryItem] = Field(default_factory=list)
