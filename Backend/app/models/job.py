from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_description: str = Field(
        ...,
        min_length=30,
        max_length=20000,
        description="Plain-text job description pasted by the user.",
        examples=[
            "We are hiring a Python developer with 3+ years of experience in FastAPI, SQL, Docker, and AWS. Bachelor's degree in Computer Science preferred."
        ],
    )
    resume_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional resume record to compare against. Defaults to the latest uploaded resume.",
    )

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Job description cannot be empty.")
        if len(normalized_value.split()) < 5:
            raise ValueError("Job description is too short to analyze.")
        return normalized_value

class JobAnalysisResponse(BaseModel):
    job_skills: list[str] = Field(default_factory=list)
    resume_skills: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    required_technologies: list[str] = Field(default_factory=list)
    experience_requirements: list[str] = Field(default_factory=list)
    education_requirements: list[str] = Field(default_factory=list)


class ResumeJobMatchResponse(BaseModel):
    match_score: int = Field(ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class MLMatchResponse(BaseModel):
    skill_match: int = Field(ge=0, le=100)
    ml_similarity: int = Field(ge=0, le=100)
