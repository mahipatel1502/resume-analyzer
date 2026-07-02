import re


class TextService:
    def clean_text(self, text: str) -> str:
        lowered_text = text.lower()
        stripped_text = re.sub(r"[^a-z0-9\s]", " ", lowered_text)
        normalized_text = re.sub(r"\s+", " ", stripped_text).strip()
        return normalized_text
