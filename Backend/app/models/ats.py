from pydantic import BaseModel, Field


class ATSScoreRequest(BaseModel):
    resume_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional resume record to score. Defaults to the latest uploaded resume.",
    )


class ATSSectionScore(BaseModel):
    score: int = Field(ge=0)
    max_score: int = Field(gt=0)
    status: str
    issues: list[str] = Field(default_factory=list)


class ATSScoreResponse(BaseModel):
    resume_id: int
    filename: str
    ats_score: int = Field(ge=0, le=100)
    sections: dict[str, ATSSectionScore]
    missing_sections: list[str] = Field(default_factory=list)
    weak_content: list[str] = Field(default_factory=list)
    formatting_issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
