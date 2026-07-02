import re

from spacy.lang.en import English

from app.repositories.skill_repository import SkillRepository
from app.services.skill_service import SkillService


class ResumeAnalysisService:
    # We keep the NLP pipeline lightweight: spaCy handles sentence segmentation, while regex handles structured patterns.
    DEGREE_PATTERNS: dict[str, tuple[str, ...]] = {
        "B.Tech": (r"\bb\.?tech(?:\b|in\b)", r"\bbachelor(?:'s)? of technology\b"),
        "M.Tech": (r"\bm\.?tech(?:\b|in\b)", r"\bmaster(?:'s)? of technology\b"),
        "BE": (r"\bb\.?e\.?\b", r"\bbachelor(?:'s)? of engineering\b"),
        "ME": (r"\bm\.?e\.?\b", r"\bmaster(?:'s)? of engineering\b"),
        "BSc": (r"\bb\.?sc\.?\b", r"\bbachelor(?:'s)? of science\b"),
        "MSc": (r"\bm\.?sc\.?\b", r"\bmaster(?:'s)? of science\b"),
        "BS": (r"\bb\.?s\.?\b", r"\bbachelor(?:'s)?\b"),
        "MS": (r"\bm\.?s\.?\b", r"\bmaster(?:'s)?\b"),
        "MBA": (r"\bmba\b", r"\bmaster(?:'s)? of business administration\b"),
        "PhD": (r"\bph\.?d\.?\b", r"\bdoctor of philosophy\b"),
    }

    UNIVERSITY_PATTERNS: tuple[str, ...] = (
        r"\b(?:University|College|Institute|School|Academy|Polytechnic)\s+of\s+[A-Z][A-Za-z&.'-]*(?:\s+[A-Z][A-Za-z&.'-]*)*\b",
        r"\b[A-Z][A-Za-z&.'-]*(?:\s+[A-Z][A-Za-z&.'-]*)*\s+(?:University|College|Institute|School|Academy|Polytechnic)\b(?:\s+of\s+[A-Z][A-Za-z&.'-]*(?:\s+[A-Z][A-Za-z&.'-]*)*)?",
        r"\b(?:IIT|NIT|IIIT|BITS)\s+[A-Z][A-Za-z&.'-]*\b",
    )

    EXPERIENCE_TYPES: dict[str, tuple[str, ...]] = {
        "Internship": (r"\binternship\b", r"\bintern\b"),
        "Freelancing Experience": (r"\bfreelanc(?:e|ing|er)\b",),
        "Work Experience": (r"\bwork experience\b", r"\bprofessional experience\b", r"\bemployment\b", r"\bfull[- ]time\b"),
    }

    YEARS_PATTERNS: tuple[str, ...] = (
        r"(?P<years>\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"(?P<years>\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience",
        r"experience\s*(?:of\s*)?(?P<years>\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"(?P<years>\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:in|with|of)\b",
        r"(?P<years>\d+)\s*[-/]\s*year(?:s)?",
    )

    MONTH_PATTERN = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )

    MONTH_MAP: dict[str, int] = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }

    EDUCATION_HEADINGS = (
        "education",
        "academic background",
        "educational qualification",
        "educational qualifications",
        "qualifications",
    )

    EXPERIENCE_HEADINGS = (
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "internship experience",
        "freelancing experience",
    )

    NORMALIZE_HEADINGS: tuple[str, ...] = (
        "professional summary",
        "technical skills",
        "internship experience",
        "work experience",
        "professional experience",
        "profile",
        "education",
        "skills",
        "projects",
        "research work",
        "certifications",
    )

    SECTION_BOUNDARY_PATTERNS: tuple[re.Pattern[str], ...] = (
        re.compile(r"(?im)^\s*(education|experience|internship experience|work experience|professional experience|projects|certifications|summary|professional summary|objective|awards|interests|skills|technical skills|technical expertise|core competencies|core skills|relevant skills|key skills)\s*$"),
        re.compile(r"^\s*[A-Z][A-Z\s/&-]{3,}\s*$", re.MULTILINE),
    )

    def __init__(self) -> None:
        self._nlp = English()
        self._nlp.add_pipe("sentencizer")
        self.skill_service = SkillService()
        self.skill_repository = SkillRepository()

    def analyze(self, text: str) -> dict[str, object]:
        text = self._normalize_text(text)
        available_skills = self.skill_repository.list_skills()
        education = self.extract_education(text)
        experience = self.extract_experience(text)
        skills = self.skill_service.extract_skills(text, available_skills)
        return {"education": education, "experience": experience, "skills": skills}

    def _normalize_text(self, text: str) -> str:
        normalized_text = text
        normalized_text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", normalized_text)
        normalized_text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", normalized_text)
        normalized_text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", normalized_text)

        for heading in sorted(self.NORMALIZE_HEADINGS, key=len, reverse=True):
            heading_pattern = r"\s+".join(re.escape(part) for part in heading.split())
            pattern = re.compile(rf"(?im)^\s*{heading_pattern}\s*$")
            normalized_text = pattern.sub(lambda m: f"\n{m.group(0).strip()}\n", normalized_text)

        normalized_text = re.sub(r"[ \t]+", " ", normalized_text)
        normalized_text = re.sub(r"\n+", "\n", normalized_text)
        return normalized_text.strip()

    def extract_education(self, text: str) -> list[dict[str, object]]:
        scan_text = self._extract_section(text, self.EDUCATION_HEADINGS) or text
        entries = self._extract_entries(scan_text, self._build_education_entry)
        return self._deduplicate_entries(entries)

    def extract_experience(self, text: str) -> list[dict[str, object]]:
        scan_text = self._extract_section(text, self.EXPERIENCE_HEADINGS) or text
        entries = self._extract_entries(scan_text, self._build_experience_entry)
        return self._deduplicate_entries(entries)

    def _extract_entries(self, text: str, builder) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        chunks = self._iter_chunks(text)
        index = 0
        while index < len(chunks):
            current_chunk = chunks[index]
            combined_chunk = ""
            if index + 1 < len(chunks):
                combined_chunk = f"{current_chunk} {chunks[index + 1]}".strip()

            parsed = None
            if combined_chunk:
                combined_candidate = builder(combined_chunk)
                if combined_candidate and self._entry_signal_count(combined_candidate) >= 2:
                    parsed = combined_candidate
                    index += 2

            if parsed is None:
                single_candidate = builder(current_chunk)
                if single_candidate:
                    parsed = single_candidate
                index += 1

            if parsed:
                entries.append(parsed)

        return entries

    def _iter_chunks(self, text: str) -> list[str]:
        chunks: list[str] = []
        for line in text.splitlines():
            cleaned_line = line.strip()
            if not cleaned_line:
                continue

            doc = self._nlp(cleaned_line)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            chunks.extend(sentences or [cleaned_line])
        return chunks

    def _build_education_entry(self, chunk: str) -> dict[str, object] | None:
        degree = self._extract_degree(chunk)
        university = self._extract_university(chunk)
        graduation_year = self._extract_graduation_year(chunk)
        if not any([degree, university, graduation_year]):
            return None
        return {"degree": degree, "university": university, "graduation_year": graduation_year, "raw_text": chunk}

    def _build_experience_entry(self, chunk: str) -> dict[str, object] | None:
        experience_type = self._extract_experience_type(chunk)
        years_of_experience = self._extract_years_of_experience(chunk)
        has_role_or_company = bool(
            re.search(r"\b(intern|engineer|developer|analyst|manager|consultant|specialist)\b", chunk, re.IGNORECASE)
            or re.search(r"\b(?:pvt\.?\s*ltd\.?|ltd\.?|inc\.?|llc|technologies|solutions|systems)\b", chunk, re.IGNORECASE)
        )
        if not any([years_of_experience, experience_type and has_role_or_company]):
            return None
        return {"experience_type": experience_type, "years_of_experience": years_of_experience, "raw_text": chunk}

    def _extract_degree(self, chunk: str) -> str | None:
        lowered_chunk = chunk.lower()
        for degree_name, patterns in self.DEGREE_PATTERNS.items():
            if any(re.search(pattern, lowered_chunk, flags=re.IGNORECASE) for pattern in patterns):
                return degree_name
        return None

    def _extract_university(self, chunk: str) -> str | None:
        normalized_chunk = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", chunk)
        normalized_chunk = re.sub(
            r"(University|College|Institute|School|Academy|Polytechnic)(?=[A-Za-z])",
            r"\1 ",
            normalized_chunk,
        )
        for pattern in self.UNIVERSITY_PATTERNS:
            match = re.search(pattern, normalized_chunk)
            if match:
                return match.group(0).strip().rstrip(".,;")
        return None

    def _extract_graduation_year(self, chunk: str) -> int | None:
        years = re.findall(r"\b(?:19|20)\d{2}\b", chunk)
        return int(years[-1]) if years else None

    def _extract_experience_type(self, chunk: str) -> str | None:
        lowered_chunk = chunk.lower()
        lowered_chunk = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", lowered_chunk)
        lowered_chunk = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", lowered_chunk)
        lowered_chunk = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", lowered_chunk)

        if "intern" in lowered_chunk:
            return "Internship"
        if "freelanc" in lowered_chunk:
            return "Freelancing Experience"

        for experience_type, patterns in self.EXPERIENCE_TYPES.items():
            if any(re.search(pattern, lowered_chunk, flags=re.IGNORECASE) for pattern in patterns):
                return experience_type
        return None

    def _extract_years_of_experience(self, chunk: str) -> float | None:
        chunk = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", chunk)
        chunk = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", chunk)
        for pattern in self.YEARS_PATTERNS:
            match = re.search(pattern, chunk, flags=re.IGNORECASE)
            if match:
                return float(match.group("years"))

        range_pattern = re.compile(
            rf"(?i)\b(?P<start_month>{self.MONTH_PATTERN})\s+(?P<start_year>\d{{4}})\s*[-–]\s*(?P<end_month>{self.MONTH_PATTERN})\s+(?P<end_year>\d{{4}}|present)\b"
        )
        range_match = range_pattern.search(chunk)
        if not range_match:
            return None

        start_month = self.MONTH_MAP.get(range_match.group("start_month").casefold())
        end_month = self.MONTH_MAP.get(range_match.group("end_month").casefold())
        if start_month is None or end_month is None:
            return None

        start_year = int(range_match.group("start_year"))
        end_year_raw = range_match.group("end_year").casefold()
        if end_year_raw == "present":
            return None

        end_year = int(end_year_raw)
        total_months = (end_year - start_year) * 12 + (end_month - start_month)
        if total_months < 0:
            return None

        # Include the ending month for a resume-style inclusive range.
        total_months += 1
        return round(total_months / 12, 2)
        return None

    def _extract_section(self, text: str, headings: tuple[str, ...]) -> str:
        lines = text.splitlines()
        heading_index = self._find_section_heading_index(lines, headings)
        if heading_index is None:
            return ""

        section_lines: list[str] = []
        for line in lines[heading_index + 1 :]:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if self._looks_like_boundary(stripped_line):
                break
            section_lines.append(stripped_line)
        return "\n".join(section_lines).strip()

    def _find_section_heading_index(self, lines: list[str], headings: tuple[str, ...]) -> int | None:
        normalized_headings = {heading.casefold() for heading in headings}
        fallback_index: int | None = None
        for index, line in enumerate(lines):
            stripped = line.strip()
            normalized = stripped.casefold().rstrip(":")
            if normalized in normalized_headings:
                if stripped and stripped == stripped.upper():
                    return index
                if fallback_index is None:
                    fallback_index = index
        return fallback_index

    def _looks_like_boundary(self, line: str) -> bool:
        normalized = line.strip()
        if not normalized:
            return False
        if any(pattern.match(normalized) for pattern in self.SECTION_BOUNDARY_PATTERNS):
            return True
        return normalized.endswith(":")

    def _deduplicate_entries(self, entries: list[dict[str, object]]) -> list[dict[str, object]]:
        seen: set[tuple[tuple[str, object], ...]] = set()
        unique_entries: list[dict[str, object]] = []
        for entry in entries:
            key = tuple(sorted((field, value) for field, value in entry.items() if field != "raw_text"))
            if key in seen:
                continue
            seen.add(key)
            unique_entries.append(entry)
        return unique_entries

    def _entry_signal_count(self, entry: dict[str, object]) -> int:
        return sum(1 for field, value in entry.items() if field != "raw_text" and value is not None)
