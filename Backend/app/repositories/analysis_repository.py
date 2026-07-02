import json

from app.database.database import get_connection, utc_now


class AnalysisRepository:
    def save_job_description(
        self,
        resume_id: int,
        job_title: str,
        company: str,
        description_text: str,
    ) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO job_descriptions (resume_id, job_title, company, description_text, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (resume_id, job_title, company, description_text, utc_now()),
            )
            return int(cursor.lastrowid)

    def get_job_description(self, jd_id: int) -> dict[str, object] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, resume_id, job_title, company, description_text, created_at
                FROM job_descriptions
                WHERE id = ?
                """,
                (jd_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "jd_id": row["id"],
            "resume_id": row["resume_id"],
            "job_title": row["job_title"],
            "company": row["company"],
            "description_text": row["description_text"],
            "created_at": row["created_at"],
        }

    def save_analysis(self, analysis_id: str, resume_id: int, jd_id: int, result: dict[str, object]) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO analyses (id, resume_id, jd_id, result_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (analysis_id, resume_id, jd_id, json.dumps(result), utc_now()),
            )

    def get_analysis(self, analysis_id: str) -> dict[str, object] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, resume_id, jd_id, result_json, created_at
                FROM analyses
                WHERE id = ?
                """,
                (analysis_id,),
            ).fetchone()

        if row is None:
            return None

        result = json.loads(row["result_json"])
        result["analysis_id"] = row["id"]
        return result

    def list_analyses(self) -> list[dict[str, object]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT a.id, a.resume_id, a.jd_id, a.result_json, a.created_at,
                       r.original_filename, j.job_title, j.company
                FROM analyses a
                JOIN resumes r ON r.id = a.resume_id
                JOIN job_descriptions j ON j.id = a.jd_id
                ORDER BY a.created_at DESC
                """
            ).fetchall()

        items: list[dict[str, object]] = []
        for row in rows:
            result = json.loads(row["result_json"])
            items.append(
                {
                    "analysis_id": row["id"],
                    "resume_id": row["resume_id"],
                    "jd_id": row["jd_id"],
                    "resume_filename": row["original_filename"],
                    "job_title": row["job_title"] or result.get("job_title", ""),
                    "company": row["company"] or result.get("company", ""),
                    "ats_score": result.get("ats_score", 0),
                    "match_score": result.get("match_score", 0),
                    "ml_score": result.get("ml_score", 0),
                    "created_at": row["created_at"],
                }
            )
        return items
