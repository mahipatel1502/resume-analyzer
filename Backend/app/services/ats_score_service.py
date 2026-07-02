import re
from pathlib import Path

from fastapi import HTTPException, status

from app.models.ats import ATSScoreRequest, ATSScoreResponse, ATSSectionScore
from app.repositories.resume_repository import ResumeRepository
from app.repositories.skill_repository import SkillRepository
from app.services.pdf_service import PDFService
from app.services.skill_service import SkillService


class ATSScoreService:
    SECTION_HEADINGS: dict[str, tuple[str, ...]] = {
        "skills": ("skills", "technical skills", "core skills", "key skills", "technical expertise"),
        "experience": ("experience", "work experience", "professional experience", "internship experience"),
        "education": ("education", "academic background", "educational qualification", "qualifications"),
        "projects": ("projects", "project experience", "academic projects", "personal projects"),
        "certifications": ("certifications", "certificates"),
    }

    SECTION_WEIGHTS: dict[str, int] = {
        "contact_information": 20,
        "skills": 20,
        "experience": 20,
        "education": 15,
        "projects": 15,
        "formatting": 10,
    }

    ACTION_VERBS: tuple[str, ...] = (
        "achieved",
        "built",
        "created",
        "delivered",
        "designed",
        "developed",
        "implemented",
        "improved",
        "increased",
        "led",
        "managed",
        "optimized",
        "reduced",
    )

    def __init__(self) -> None:
        self.resume_repository = ResumeRepository()
        self.pdf_service = PDFService()
        self.skill_repository = SkillRepository()
        self.skill_service = SkillService()

    def score_resume(self, request: ATSScoreRequest) -> ATSScoreResponse:
        resume_record = self._resolve_resume_record(request.resume_id)
        resume_text = self._resolve_resume_text(resume_record)
        sections = self._extract_sections(resume_text)

        section_scores = {
            "contact_information": self._score_contact_information(resume_text),
            "skills": self._score_skills(resume_text, sections),
            "experience": self._score_experience(sections),
            "education": self._score_education(sections),
            "projects": self._score_projects(sections),
            "formatting": self._score_formatting(resume_text),
        }
        ats_score = min(100, sum(section.score for section in section_scores.values()))
        missing_sections = self._missing_sections(section_scores)
        weak_content = self._weak_content(section_scores)
        formatting_issues = section_scores["formatting"].issues

        return ATSScoreResponse(
            resume_id=int(resume_record["resume_id"]),
            filename=str(resume_record["filename"]),
            ats_score=ats_score,
            sections=section_scores,
            missing_sections=missing_sections,
            weak_content=weak_content,
            formatting_issues=formatting_issues,
            suggestions=self._build_suggestions(section_scores, missing_sections),
        )

    def _resolve_resume_record(self, resume_id: int | None) -> dict[str, object]:
        file_record = self.resume_repository.get_resume_file_record(resume_id)
        if file_record is None:
            detail = "Resume not found." if resume_id else "No uploaded resume found. Upload a resume first."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

        payload = self.resume_repository.get_resume_payload(resume_id)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume analysis not found.")

        return {**payload, **file_record}

    def _resolve_resume_text(self, resume_record: dict[str, object]) -> str:
        file_path = Path(str(resume_record.get("file_path", "")))
        if file_path.exists():
            try:
                extracted_text = self.pdf_service.extract_text(file_path)
                if extracted_text.strip():
                    return extracted_text
            except Exception:
                pass

        extracted_text = str(resume_record.get("extracted_text", "")).strip()
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Resume text is empty. Re-upload the resume.",
            )
        return extracted_text

    def _score_contact_information(self, text: str) -> ATSSectionScore:
        issues: list[str] = []
        score = 0
        contact_area = "\n".join(text.splitlines()[:12])
        normalized_contact_area = re.sub(r"\s+", " ", contact_area).strip()

        if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", normalized_contact_area, re.IGNORECASE):
            score += 5
        else:
            issues.append("Missing email address.")

        if re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", normalized_contact_area):
            score += 5
        else:
            issues.append("Missing phone number.")

        if re.search(r"\blinked\s*in\b|linkedin\.com(?:/in)?|linkedin\s*[:/-]", normalized_contact_area, re.IGNORECASE):
            score += 5
        else:
            issues.append("Missing LinkedIn profile.")

        if re.search(r"\bgithub\b|github\.com|github\s*[:/-]", normalized_contact_area, re.IGNORECASE):
            score += 5
        else:
            issues.append("Missing GitHub profile.")

        return self._section_score(score, "contact_information", issues)

    def _score_skills(self, text: str, sections: dict[str, str]) -> ATSSectionScore:
        issues: list[str] = []
        skills_section = sections.get("skills", "")
        if not skills_section:
            issues.append("Missing skills section.")

        available_skills = self.skill_repository.list_skills()
        extracted_skills = self.skill_service.extract_skills(text, available_skills)
        score = 0
        if skills_section:
            score += 8
        if len(extracted_skills) >= 8:
            score += 8
        elif len(extracted_skills) >= 4:
            score += 5
            issues.append("Skills section could include more role-relevant skills.")
        else:
            issues.append("Skills section is weak or too short.")

        if self._has_grouped_skills(skills_section):
            score += 4
        elif skills_section:
            issues.append("Group skills by type, such as languages, frameworks, tools, and databases.")

        return self._section_score(score, "skills", issues)

    def _score_experience(self, sections: dict[str, str]) -> ATSSectionScore:
        issues: list[str] = []
        experience_text = sections.get("experience", "")
        if not experience_text:
            return self._section_score(0, "experience", ["Missing experience section."])

        score = 8
        if re.search(r"\b(?:19|20)\d{2}\b|present|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", experience_text, re.IGNORECASE):
            score += 4
        else:
            issues.append("Experience entries should include dates.")

        if self._contains_action_verb(experience_text):
            score += 4
        else:
            issues.append("Experience section needs stronger action verbs.")

        if re.search(r"\d+%|\$\d+|\b\d+\+?\s*(?:users|clients|projects|models|apis|reports|hours)\b", experience_text, re.IGNORECASE):
            score += 4
        else:
            issues.append("Experience section should include measurable achievements.")

        return self._section_score(score, "experience", issues)

    def _score_education(self, sections: dict[str, str]) -> ATSSectionScore:
        issues: list[str] = []
        education_text = sections.get("education", "")
        if not education_text:
            return self._section_score(0, "education", ["Missing education section."])

        score = 7
        if re.search(r"\b(bachelor|master|phd|b\.?tech|m\.?tech|b\.?sc|m\.?sc|degree|diploma)\b", education_text, re.IGNORECASE):
            score += 4
        else:
            issues.append("Education section should include degree name.")

        if re.search(r"\b(university|college|institute|school)\b", education_text, re.IGNORECASE):
            score += 4
        else:
            issues.append("Education section should include institution name.")

        return self._section_score(score, "education", issues)

    def _score_projects(self, sections: dict[str, str]) -> ATSSectionScore:
        issues: list[str] = []
        projects_text = sections.get("projects", "")
        if not projects_text:
            return self._section_score(0, "projects", ["Missing projects section."])

        score = 6
        project_lines = [line for line in projects_text.splitlines() if line.strip()]
        if len(project_lines) >= 3:
            score += 3
        else:
            issues.append("Add project descriptions, not only project titles.")

        if self._contains_action_verb(projects_text):
            score += 3
        else:
            issues.append("Project descriptions should explain what you built or improved.")

        if self.skill_service.extract_skills(projects_text, self.skill_repository.list_skills()):
            score += 3
        else:
            issues.append("Project descriptions should mention technologies used.")

        return self._section_score(score, "projects", issues)

    def _score_formatting(self, text: str) -> ATSSectionScore:
        issues: list[str] = []
        score = self.SECTION_WEIGHTS["formatting"]
        lines = [line for line in text.splitlines() if line.strip()]

        if len(text.split()) < 120:
            score -= 3
            issues.append("Resume text is too short for ATS screening.")

        if any(len(line) > 160 for line in lines):
            score -= 2
            issues.append("Some lines are too long; use shorter bullets for ATS readability.")

        special_character_count = len(re.findall(r"[^\w\s@.+/#(),:&|-]", text))
        if special_character_count > max(20, len(text) * 0.03):
            score -= 2
            issues.append("Resume has too many special characters or decorative symbols.")

        if not self._has_standard_headings(text):
            score -= 3
            issues.append("Use standard section headings like Skills, Experience, Education, and Projects.")

        return self._section_score(max(0, score), "formatting", issues)

    def _extract_sections(self, text: str) -> dict[str, str]:
        lines = text.splitlines()
        sections: dict[str, list[str]] = {}
        current_section: str | None = None

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            heading = self._canonical_heading(stripped_line)
            if heading:
                current_section = heading
                sections.setdefault(current_section, [])
                continue

            if current_section:
                sections[current_section].append(stripped_line)

        return {section: "\n".join(section_lines).strip() for section, section_lines in sections.items()}

    def _canonical_heading(self, line: str) -> str | None:
        normalized_line = re.sub(r"[:\s]+$", "", line.casefold())
        for section, headings in self.SECTION_HEADINGS.items():
            if normalized_line in headings:
                return section
        return None

    def _has_grouped_skills(self, skills_section: str) -> bool:
        return bool(
            re.search(
                r"\b(languages|frameworks|tools|databases|technologies|libraries|cloud)\b\s*:",
                skills_section,
                re.IGNORECASE,
            )
        )

    def _contains_action_verb(self, text: str) -> bool:
        return any(re.search(rf"\b{verb}\b", text, re.IGNORECASE) for verb in self.ACTION_VERBS)

    def _has_standard_headings(self, text: str) -> bool:
        found_sections = self._extract_sections(text)
        return len({"skills", "education", "projects"} & set(found_sections)) >= 2

    def _section_score(self, score: int, section_name: str, issues: list[str]) -> ATSSectionScore:
        max_score = self.SECTION_WEIGHTS[section_name]
        bounded_score = min(max_score, max(0, score))
        if bounded_score == 0:
            status = "missing"
        elif issues:
            status = "needs_improvement"
        else:
            status = "good"
        return ATSSectionScore(score=bounded_score, max_score=max_score, status=status, issues=issues)

    def _missing_sections(self, sections: dict[str, ATSSectionScore]) -> list[str]:
        return [
            section.replace("_", " ").title()
            for section, score in sections.items()
            if score.status == "missing" and section != "formatting"
        ]

    def _weak_content(self, sections: dict[str, ATSSectionScore]) -> list[str]:
        weak_items: list[str] = []
        for section, score in sections.items():
            if section == "formatting":
                continue
            if score.status == "needs_improvement":
                weak_items.extend(score.issues)
        return weak_items

    def _build_suggestions(self, sections: dict[str, ATSSectionScore], missing_sections: list[str]) -> list[str]:
        suggestions: list[str] = []
        issue_text = " ".join(issue for section in sections.values() for issue in section.issues).casefold()

        if "github" in issue_text:
            suggestions.append("Add GitHub profile.")
        if "linkedin" in issue_text:
            suggestions.append("Add LinkedIn profile.")
        if "measurable achievements" in issue_text:
            suggestions.append("Add measurable achievements with numbers, percentages, or impact.")
        if "action verbs" in issue_text:
            suggestions.append("Start experience bullets with strong action verbs.")
        if "project descriptions" in issue_text or "technologies used" in issue_text:
            suggestions.append("Add project descriptions with technologies and outcomes.")
        if "skills section" in issue_text or "group skills" in issue_text:
            suggestions.append("Add a clear technical skills section with role-relevant keywords.")
        if "group skills" in issue_text:
            suggestions.append("Group skills by languages, frameworks, tools, databases, and cloud.")
        if "dates" in issue_text:
            suggestions.append("Add dates for each experience entry.")
        if "standard section headings" in issue_text:
            suggestions.append("Use standard ATS-friendly section headings.")

        for missing_section in missing_sections:
            suggestions.append(f"Add {missing_section} section.")

        if not suggestions:
            suggestions.append("Resume is ATS-friendly. Keep tailoring keywords to each job description.")

        return self._deduplicate(suggestions)

    def _deduplicate(self, values: list[str]) -> list[str]:
        deduplicated_values: list[str] = []
        seen_values: set[str] = set()
        for value in values:
            normalized_value = value.casefold()
            if normalized_value in seen_values:
                continue
            seen_values.add(normalized_value)
            deduplicated_values.append(value)
        return deduplicated_values
