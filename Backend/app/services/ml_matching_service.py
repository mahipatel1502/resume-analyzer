import re

from fastapi import HTTPException, status
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MLMatchingService:
    def calculate_similarity(self, resume_text: str, job_description: str) -> int:
        cleaned_resume_text = self._preprocess_text(resume_text)
        cleaned_job_description = self._preprocess_text(job_description)

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

    def _preprocess_text(self, text: str) -> str:
        normalized_text = text.casefold()
        normalized_text = re.sub(r"[^a-z0-9+#.\s-]", " ", normalized_text)
        normalized_text = re.sub(r"\s+", " ", normalized_text)
        return normalized_text.strip()
