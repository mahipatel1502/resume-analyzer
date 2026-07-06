import re

from fastapi import HTTPException, status
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MLMatchingService:
    def calculate_similarity(self, resume_text: str, job_description: str) -> int:
        cleaned_resume_text = self._prepare_relevant_text(resume_text)
        cleaned_job_description = self._prepare_relevant_text(job_description)

        if not cleaned_resume_text or not cleaned_job_description:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Resume text and job description must contain analyzable text.",
            )

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            lowercase=True,
            max_features=5000,
        )
        tfidf_matrix = vectorizer.fit_transform([cleaned_resume_text, cleaned_job_description])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(similarity * 100)

    def _prepare_relevant_text(self, text: str) -> str:
        sections = self._extract_sections(text)
        relevant_parts = [
            sections.get("skills", ""),
            sections.get("experience", ""),
            sections.get("projects", ""),
        ]

        combined_sections = " ".join(part for part in relevant_parts if part.strip())
        if combined_sections.strip():
            return self._preprocess_text(combined_sections)

        return self._preprocess_text(text)

    def _preprocess_text(self, text: str) -> str:
        normalized_text = text.casefold()
        normalized_text = re.sub(r"[^a-z0-9+#.\s-]", " ", normalized_text)
        normalized_text = re.sub(r"\s+", " ", normalized_text)
        return normalized_text.strip()

    def _extract_sections(self, text: str) -> dict[str, str]:
        section_headings: dict[str, tuple[str, ...]] = {
            "skills": ("skills", "technical skills", "core skills", "key skills", "technical expertise"),
            "experience": ("experience", "work experience", "professional experience", "internship experience"),
            "projects": ("projects", "project experience", "academic projects", "personal projects"),
        }

        lines = text.splitlines()
        sections: dict[str, list[str]] = {}
        current_section: str | None = None

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            heading = self._canonical_heading(stripped_line, section_headings)
            if heading:
                current_section = heading
                sections.setdefault(current_section, [])
                continue

            if current_section:
                sections[current_section].append(stripped_line)

        return {section: "\n".join(section_lines).strip() for section, section_lines in sections.items()}

    def _canonical_heading(self, line: str, section_headings: dict[str, tuple[str, ...]]) -> str | None:
        normalized_line = re.sub(r"[:\s]+$", "", line.casefold())
        for section, headings in section_headings.items():
            if normalized_line in headings:
                return section
        return None
