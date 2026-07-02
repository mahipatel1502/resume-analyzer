import re

import nltk
from nltk import word_tokenize


class SkillService:
    SKILL_PATTERNS: dict[str, list[str]] = {
        "Python": [r"\bpython\b"],
        "Java": [r"\bjava\b"],
        "JavaScript": [r"\bjavascript\b", r"\bjava script\b", r"\bjs\b"],
        "C++": [r"\bc\+\+\b", r"\bcpp\b", r"\bc plus plus\b"],
        "SQL": [r"\bsql\b"],
        "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
        "Data Analysis": [r"\bdata analysis\b"],
        "Deep Learning": [r"\bdeep learning\b"],
        "TensorFlow": [r"\btensorflow\b", r"\btensor flow\b"],
        "PyTorch": [r"\bpytorch\b", r"\bpy torch\b"],
        "Pandas": [r"\bpandas\b"],
        "NumPy": [r"\bnumpy\b", r"\bnum py\b"],
        "Scikit-learn": [r"\bscikit-learn\b", r"\bscikit learn\b", r"\bsklearn\b"],
        "NLP": [r"\bnlp\b", r"\bnatural language processing\b"],
        "React": [r"\breact\b(?!\.?\s*js)"],
        "React.js": [r"\breact\.?js\b", r"\breact js\b"],
        "Node.js": [r"\bnode\.?js\b", r"\bnode js\b", r"\bnodejs\b"],
        "Express.js": [r"\bexpress\.?js\b", r"\bexpress js\b"],
        "MySQL": [r"\bmysql\b", r"\bmy sql\b"],
        "MongoDB": [r"\bmongodb\b", r"\bmongo db\b"],
        "Docker": [r"\bdocker\b"],
        "AWS": [r"\baws\b"],
        "Git": [r"\bgit\b"],
        "GitHub": [r"\bgithub\b", r"\bgit hub\b"],
    }

    SKILL_LINE_LABELS: set[str] = {
        "programming languages",
        "ai/ml",
        "ai ml",
        "web technology",
        "web technologies",
        "database",
        "databases",
        "frameworks",
        "tools",
        "technologies",
        "technology used",
    }

    SPLIT_PATTERN = re.compile(r"[,;|•·]")

    GENERIC_FILTER_WORDS: set[str] = {
        "experience",
        "summary",
        "project",
        "projects",
        "education",
        "skills",
        "work",
        "worked",
        "using",
        "developed",
        "built",
        "created",
        "implemented",
        "designed",
        "responsible",
        "senior",
        "junior",
        "lead",
        "principal",
        "staff",
        "software",
        "engineer",
        "developer",
        "analyst",
        "manager",
        "architect",
        "consultant",
        "specialist",
        "associate",
        "intern",
        "software",
        "engineer",
        "application",
        "applications",
        "team",
        "teams",
        "database",
        "data",
        "model",
        "models",
        "resume",
        "profile",
        "analysis",
        "objective",
        "summary",
        "professional",
        "familiar",
        "knowledge",
    }

    SECTION_HEADINGS: tuple[str, ...] = (
        "skills",
        "technical skills",
        "technical expertise",
        "core competencies",
        "core skills",
        "relevant skills",
        "key skills",
    )

    NORMALIZE_HEADINGS: tuple[str, ...] = (
        "technical skills",
        "professional summary",
        "profile",
        "education",
        "skills",
        "projects",
        "research work",
        "certifications",
    )

    SECTION_BOUNDARY_PATTERNS: tuple[re.Pattern[str], ...] = (
        re.compile(
            r"(?im)^\s*(education|experience|internship experience|work experience|professional experience|projects|project experience|certifications|summary|professional summary|objective|awards|interests)\s*$"
        ),
        re.compile(r"^\s*[A-Z][A-Z\s/&-]{3,}\s*$", re.MULTILINE),
    )

    def __init__(self) -> None:
        self._ensure_nltk_resources()

    def _ensure_nltk_resources(self) -> None:
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            try:
                nltk.download("punkt", quiet=True)
            except Exception:
                pass

    def extract_skills(self, text: str, available_skills: list[str] | None = None) -> list[str]:
        available_skills = available_skills or []
        normalized_text = self._normalize_text(text)
        skills_section = self._extract_skills_section(normalized_text)
        scan_text = skills_section or text
        lowered_text = scan_text.lower()
        lowered_full_text = text.lower()
        try:
            word_tokenize(lowered_text)
        except LookupError:
            self._ensure_nltk_resources()
        detected_skills: list[str] = []
        seen_skills: set[str] = set()

        for skill in available_skills:
            if self._matches_skill(skill, lowered_full_text):
                self._append_unique(detected_skills, seen_skills, skill)

        if skills_section:
            section_candidates = self._extract_section_candidates(skills_section)
            for candidate in section_candidates:
                canonical_skill = self._standardize_candidate(candidate, available_skills)
                if canonical_skill:
                    self._append_unique(detected_skills, seen_skills, canonical_skill)

        return detected_skills

    def _normalize_text(self, text: str) -> str:
        normalized_text = text

        # Recover spacing from compacted tokens like "BTechin" or "may2025".
        normalized_text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", normalized_text)
        normalized_text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", normalized_text)
        normalized_text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", normalized_text)

        # Add line breaks around major headings so section slicing stays stable.
        for heading in sorted(self.NORMALIZE_HEADINGS, key=len, reverse=True):
            heading_pattern = r"\s+".join(re.escape(part) for part in heading.split())
            pattern = re.compile(rf"(?im)^\s*{heading_pattern}\s*$")
            normalized_text = pattern.sub(lambda m: f"\n{m.group(0).strip()}\n", normalized_text)

        normalized_text = re.sub(r"[ \t]+", " ", normalized_text)
        normalized_text = re.sub(r"\n+", "\n", normalized_text)
        return normalized_text.strip()

    def _extract_skills_section(self, text: str) -> str:
        lines = text.splitlines()
        if not lines:
            return ""

        heading_index = self._find_section_heading_index(lines)
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

    def _find_section_heading_index(self, lines: list[str]) -> int | None:
        fallback_index: int | None = None
        for index, line in enumerate(lines):
            stripped = line.strip()
            normalized = stripped.casefold().rstrip(":")
            if normalized in self.SECTION_HEADINGS:
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

        if normalized.endswith(":"):
            return True

        return False

    def _matches_skill(self, skill: str, lowered_text: str) -> bool:
        patterns = self.SKILL_PATTERNS.get(skill, [rf"\b{re.escape(skill.lower())}\b"])
        return any(re.search(pattern, lowered_text) for pattern in patterns)

    def _extract_section_candidates(self, text: str) -> list[str]:
        candidates: list[str] = []
        for line in text.splitlines():
            normalized_line = line.strip()
            if not normalized_line:
                continue

            content = normalized_line
            if ":" in normalized_line:
                label, value = normalized_line.split(":", 1)
                compact_label = re.sub(r"\s+", "", label.strip().casefold())
                normalized_labels = {re.sub(r"\s+", "", item) for item in self.SKILL_LINE_LABELS}
                if label.strip().casefold() in self.SKILL_LINE_LABELS or compact_label in normalized_labels:
                    content = value.strip()

            raw_parts = [part.strip() for part in self.SPLIT_PATTERN.split(content) if part.strip()]
            for raw_part in raw_parts:
                if "/" in raw_part and raw_part.casefold() not in {"node.js"}:
                    slash_parts = [part.strip() for part in raw_part.split("/") if part.strip()]
                    candidates.extend(slash_parts)
                else:
                    candidates.append(raw_part)

        return [candidate for candidate in candidates if self._is_useful_candidate(candidate)]

    def _is_useful_candidate(self, candidate: str) -> bool:
        normalized = candidate.strip().casefold()
        if not normalized:
            return False

        normalized = re.sub(r"\s+", " ", normalized).strip()

        if normalized in self.GENERIC_FILTER_WORDS:
            return False

        candidate_tokens = re.findall(r"[a-z0-9+#.-]+", normalized)
        if candidate_tokens and any(token in self.GENERIC_FILTER_WORDS for token in candidate_tokens):
            return False

        if len(candidate_tokens) > 3:
            return False

        if candidate_tokens and candidate_tokens[0] in {"in", "with", "and", "or", "strong"}:
            return False

        if len(normalized) < 2:
            return False

        if re.fullmatch(r"[\d\W_]+", normalized):
            return False

        return True

    def _standardize_candidate(self, candidate: str, available_skills: list[str]) -> str | None:
        normalized_candidate = candidate.casefold()

        for skill in available_skills:
            if self._matches_candidate_to_skill(normalized_candidate, skill):
                return skill

        return candidate.strip()

    def _matches_candidate_to_skill(self, normalized_candidate: str, skill: str) -> bool:
        normalized_skill = skill.casefold()
        if normalized_candidate == normalized_skill:
            return True

        patterns = self.SKILL_PATTERNS.get(skill, [])
        return any(re.fullmatch(pattern, normalized_candidate, flags=re.IGNORECASE) for pattern in patterns)

    def _append_unique(self, target: list[str], seen_skills: set[str], skill: str) -> None:
        normalized_skill = skill.casefold()
        if normalized_skill in seen_skills:
            return

        seen_skills.add(normalized_skill)
        target.append(skill)
