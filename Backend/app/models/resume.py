from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    degree: str | None = None
    university: str | None = None
    graduation_year: int | None = None
    raw_text: str | None = None


class ExperienceEntry(BaseModel):
    experience_type: str | None = None
    years_of_experience: float | None = None
    raw_text: str | None = None


class ResumeAnalysisResponse(BaseModel):
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    message: str
    resume_id: int
    filename: str
    extracted_text: str
    analysis: ResumeAnalysisResponse


class ResumeRecord(BaseModel):
    resume_id: int
    filename: str
    extracted_text: str
    extracted_skills: list[str]
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    created_at: str


class ResumeSkillsResponse(BaseModel):
    resumes: list[ResumeRecord]


class EducationResponse(BaseModel):
    resume_id: int
    filename: str
    education: list[EducationEntry] = Field(default_factory=list)


class ExperienceResponse(BaseModel):
    resume_id: int
    filename: str
    experience: list[ExperienceEntry] = Field(default_factory=list)
