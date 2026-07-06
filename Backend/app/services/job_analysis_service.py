import re
from pathlib import Path

from fastapi import HTTPException, status

from app.models.job import JobAnalysisRequest, JobAnalysisResponse, MLMatchResponse, ResumeJobMatchResponse
from app.repositories.resume_repository import ResumeRepository
from app.repositories.skill_repository import SkillRepository
from app.services.pdf_service import PDFService
from app.services.ml_matching_service import MLMatchingService
from app.services.skill_service import SkillService


class JobAnalysisService:
    TECHNOLOGY_PATTERNS: dict[str, list[str]] = {
        "FastAPI": [r"\bfastapi\b", r"\bfast api\b"],
        "Flask": [r"\bflask\b"],
        "Django": [r"\bdjango\b"],
        "Spring Boot": [r"\bspring boot\b"],
        "Express.js": [r"\bexpress\.?js\b", r"\bexpress js\b"],
        "Angular": [r"\bangular\b"],
        "Vue.js": [r"\bvue\.?js\b", r"\bvue js\b"],
        "Next.js": [r"\bnext\.?js\b", r"\bnext js\b"],
        "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
        "MySQL": [r"\bmysql\b"],
        "MongoDB": [r"\bmongodb\b", r"\bmongo db\b"],
        "Redis": [r"\bredis\b"],
        "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
        "Azure": [r"\bazure\b"],
        "Google Cloud": [r"\bgoogle cloud\b", r"\bgcp\b"],
        "CI/CD": [r"\bci/cd\b", r"\bci cd\b", r"\bcontinuous integration\b"],
        "Linux": [r"\blinux\b"],
        "REST API": [r"\brest api\b", r"\brestful\b"],
        "GraphQL": [r"\bgraphql\b"],
    }

    EXPERIENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
        re.compile(
            r"\b(?:minimum\s+)?\d+\+?\s*(?:-\s*\d+\+?\s*)?(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bexperience\s+(?:with|in|using|building|developing|working\s+with)\s+[^.;\n]+",
            re.IGNORECASE,
        ),
        re.compile(r"\b(?:entry|junior|mid|senior|lead|principal)[-\s]+level\b", re.IGNORECASE),
    )

    EDUCATION_PATTERNS: tuple[re.Pattern[str], ...] = (
        re.compile(
            r"\b(?:bachelor'?s?|master'?s?|phd|doctorate|degree|diploma)\b[^.;\n]*",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:computer science|information technology|software engineering|engineering|mathematics|statistics|data science)\b[^.;\n]*",
            re.IGNORECASE,
        ),
    )

    REQUIREMENT_HINTS: tuple[str, ...] = (
        "skills",
        "skill set",
        "skillset",
        "technologies",
        "technology",
        "tools",
        "stack",
        "requirements",
        "qualifications",
        "must have",
        "required",
        "preferred",
        "experience with",
        "experience in",
        "proficiency in",
        "familiar with",
        "knowledge of",
        "work with",
        "using",
    )

    SPLIT_PATTERN: re.Pattern[str] = re.compile(r"[,;|/•·]")

    def __init__(self) -> None:
        self.resume_repository = ResumeRepository()
        self.skill_repository = SkillRepository()
        self.pdf_service = PDFService()
        self.skill_service = SkillService()
        self.ml_matching_service = MLMatchingService()

    def analyze_job(self, request: JobAnalysisRequest, user_id: int) -> JobAnalysisResponse:
        cleaned_job_description = self._preprocess_job_description(request.job_description)
        resume_skills = self._resolve_resume_skills(request, user_id)
        available_skills = self._build_available_skills(cleaned_job_description, resume_skills)
        job_skills = self.skill_service.extract_skills(cleaned_job_description, available_skills)
        required_technologies = self._extract_required_technologies(cleaned_job_description, available_skills)
        job_skills = self._deduplicate_preserving_order([*job_skills, *required_technologies])
        matched_skills, missing_skills = self._compare_skills(job_skills, resume_skills)

        return JobAnalysisResponse(
            job_skills=job_skills,
            resume_skills=resume_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            required_technologies=required_technologies,
            experience_requirements=self._extract_matches(cleaned_job_description, self.EXPERIENCE_PATTERNS),
            education_requirements=self._extract_matches(cleaned_job_description, self.EDUCATION_PATTERNS),
        )

    def match_resume(self, request: JobAnalysisRequest, user_id: int) -> ResumeJobMatchResponse:
        analysis = self.analyze_job(request, user_id)
        match_score = self._calculate_skill_match_score(analysis.job_skills, analysis.matched_skills)

        return ResumeJobMatchResponse(
            match_score=match_score,
            matched_skills=analysis.matched_skills,
            missing_skills=analysis.missing_skills,
            recommendations=self._build_recommendations(analysis.missing_skills),
        )

    def ml_match(self, request: JobAnalysisRequest, user_id: int) -> MLMatchResponse:
        analysis = self.analyze_job(request, user_id)
        resume_text = self._resolve_resume_text_for_ml(request, user_id)
        ml_similarity = self.ml_matching_service.calculate_similarity(resume_text, request.job_description)

        return MLMatchResponse(
            skill_match=self._calculate_skill_match_score(analysis.job_skills, analysis.matched_skills),
            ml_similarity=ml_similarity,
        )

    def _preprocess_job_description(self, job_description: str) -> str:
        cleaned_text = re.sub(r"\r\n?", "\n", job_description)
        cleaned_text = re.sub(r"[•·]", "\n- ", cleaned_text)
        cleaned_text = re.sub(r"(?i)\b(job description|responsibilities|requirements|qualifications)\s*:", r"\n\1:\n", cleaned_text)
        cleaned_text = re.sub(r"(?i)\b(must have|required skills|key skills|technical skills|preferred skills)\s*:", r"\n\1:\n", cleaned_text)
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
        return cleaned_text.strip()

    def _build_available_skills(self, job_description: str, resume_skills: list[str]) -> list[str]:
        known_skills = self.skill_repository.list_skills()
        technology_names = list(self.TECHNOLOGY_PATTERNS.keys())
        section_candidates = self._extract_requirement_candidates(job_description)
        text_candidates = self._extract_requirement_candidates_from_text(job_description)
        return self._deduplicate_preserving_order(
            [*known_skills, *technology_names, *resume_skills, *section_candidates, *text_candidates]
        )

    def _resolve_resume_skills(self, request: JobAnalysisRequest, user_id: int) -> list[str]:
        resume_payload = self.resume_repository.get_resume_payload(user_id, request.resume_id)
        if resume_payload is None:
            detail = "Resume not found." if request.resume_id else "No uploaded resume found. Upload a resume first."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

        extracted_skills = resume_payload.get("extracted_skills", [])
        if not isinstance(extracted_skills, list):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stored resume skills are invalid.",
            )
        return self._deduplicate_preserving_order([str(skill) for skill in extracted_skills if str(skill).strip()])

    def _resolve_resume_text(self, request: JobAnalysisRequest, user_id: int) -> str:
        resume_payload = self.resume_repository.get_resume_payload(user_id, request.resume_id)
        if resume_payload is None:
            detail = "Resume not found." if request.resume_id else "No uploaded resume found. Upload a resume first."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

        resume_text = resume_payload.get("extracted_text", "")
        if not isinstance(resume_text, str) or not resume_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Stored resume text is empty. Re-upload or reanalyze the resume.",
            )
        return resume_text

    def _resolve_resume_text_for_ml(self, request: JobAnalysisRequest, user_id: int) -> str:
        file_record = self.resume_repository.get_resume_file_record(user_id, request.resume_id)
        if file_record is not None:
            file_path = Path(str(file_record["file_path"]))
            if file_path.exists():
                try:
                    extracted_text = self.pdf_service.extract_text(file_path)
                    if extracted_text.strip():
                        return extracted_text
                except Exception:
                    pass

        return self._resolve_resume_text(request, user_id)

    def _extract_required_technologies(self, text: str, available_skills: list[str]) -> list[str]:
        lowered_text = text.casefold()
        technologies: list[str] = []
        for technology, patterns in self.TECHNOLOGY_PATTERNS.items():
            if any(re.search(pattern, lowered_text, flags=re.IGNORECASE) for pattern in patterns):
                technologies.append(technology)

        for skill in available_skills:
            pattern = rf"\b{re.escape(skill.casefold())}\b"
            if re.search(pattern, lowered_text) and self._looks_like_technology(skill):
                technologies.append(skill)

        return self._deduplicate_preserving_order(technologies)

    def _extract_requirement_candidates(self, text: str) -> list[str]:
        candidates: list[str] = []
        for line in text.splitlines():
            normalized_line = line.strip(" -•\t")
            if not normalized_line:
                continue

            if self._looks_like_requirement_line(normalized_line):
                candidates.extend(self._split_candidate_line(normalized_line))
        return self._canonicalize_candidates(candidates)

    def _extract_requirement_candidates_from_text(self, text: str) -> list[str]:
        candidates: list[str] = []
        for raw_line in text.splitlines():
            normalized_line = raw_line.strip(" -•\t")
            if not normalized_line:
                continue

            if self._looks_like_requirement_line(normalized_line):
                candidates.extend(self._split_candidate_line(normalized_line))
                continue

            if any(hint in normalized_line.casefold() for hint in self.REQUIREMENT_HINTS):
                candidates.extend(self._split_candidate_line(normalized_line))

        return self._canonicalize_candidates(candidates)

    def _looks_like_requirement_line(self, line: str) -> bool:
        return bool(re.search(r"(?i)\b(skills?|skill set|skillset|technologies|technology|tools|stack|requirements?|qualifications?|must have|required|preferred)\b", line))

    def _split_candidate_line(self, line: str) -> list[str]:
        if ":" in line:
            line = line.split(":", 1)[1]
        parts = [part.strip(" .") for part in self.SPLIT_PATTERN.split(line) if part.strip(" .")]
        if len(parts) <= 1:
            return parts

        flattened: list[str] = []
        for part in parts:
            flattened.extend([piece.strip(" .") for piece in re.split(r"\band\b|\bor\b", part, flags=re.IGNORECASE) if piece.strip(" .")])
        return flattened

    def _canonicalize_candidates(self, candidates: list[str]) -> list[str]:
        available_skills = self.skill_repository.list_skills()
        canonical_candidates: list[str] = []
        for candidate in candidates:
            cleaned_candidate = re.sub(r"\s+", " ", candidate).strip()
            if not self._is_candidate_skill(cleaned_candidate):
                continue

            canonical_candidate = self.skill_service._standardize_candidate(cleaned_candidate, available_skills)
            if canonical_candidate:
                canonical_candidates.append(canonical_candidate)

        return self._deduplicate_preserving_order(canonical_candidates)

    def _is_candidate_skill(self, candidate: str) -> bool:
        normalized_candidate = candidate.casefold().strip()
        if not normalized_candidate or len(normalized_candidate) > 40:
            return False
        if re.fullmatch(r"(?:and|or|with|for|of|the|to|a|an)", normalized_candidate):
            return False
        return not any(
            phrase in normalized_candidate
            for phrase in (
                "experience",
                "responsible",
                "preferred",
                "required",
                "candidate",
                "ability",
                "degree",
            )
        )

    def _extract_matches(self, text: str, patterns: tuple[re.Pattern[str], ...]) -> list[str]:
        matches: list[str] = []
        for pattern in patterns:
            for match in pattern.finditer(text):
                value = re.sub(r"\s+", " ", match.group(0)).strip(" .;,")
                if value:
                    matches.append(value)
        return self._deduplicate_preserving_order(matches)

    def _compare_skills(self, job_skills: list[str], resume_skills: list[str]) -> tuple[list[str], list[str]]:
        normalized_resume_skills = {self._normalize_skill(skill) for skill in resume_skills}
        matched_skills: list[str] = []
        missing_skills: list[str] = []

        for job_skill in job_skills:
            if self._normalize_skill(job_skill) in normalized_resume_skills:
                matched_skills.append(job_skill)
            else:
                missing_skills.append(job_skill)

        return matched_skills, missing_skills

    def _build_recommendations(self, missing_skills: list[str]) -> list[str]:
        if not missing_skills:
            return ["Your resume matches all extracted job skills."]

        if len(missing_skills) == 1:
            return [f"Learn {missing_skills[0]}."]

        skill_list = ", ".join(missing_skills[:-1])
        return [f"Learn {skill_list} and {missing_skills[-1]}."]

    def _calculate_skill_match_score(self, job_skills: list[str], matched_skills: list[str]) -> int:
        if not job_skills:
            return 0
        return round((len(matched_skills) / len(job_skills)) * 100)

    def _looks_like_technology(self, skill: str) -> bool:
        return bool(re.search(r"[A-Z+#.]|\b(api|sql|cloud|docker|kubernetes|react|node|python|java|git|aws)\b", skill))

    def _normalize_skill(self, skill: str) -> str:
        return re.sub(r"[^a-z0-9+#]+", "", skill.casefold())

    def _deduplicate_preserving_order(self, values: list[str]) -> list[str]:
        deduplicated_values: list[str] = []
        seen_values: set[str] = set()
        for value in values:
            cleaned_value = re.sub(r"\s+", " ", value).strip()
            if not cleaned_value:
                continue

            normalized_value = self._normalize_skill(cleaned_value)
            if normalized_value in seen_values:
                continue

            seen_values.add(normalized_value)
            deduplicated_values.append(cleaned_value)
        return deduplicated_values
