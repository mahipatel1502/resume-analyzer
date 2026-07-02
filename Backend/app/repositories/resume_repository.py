import json

from pathlib import Path

from app.database.database import get_connection, serialize_skills, utc_now


class ResumeRepository:
    def save_resume(
        self,
        original_filename: str,
        stored_filename: str,
        file_path: str,
        extracted_text: str,
        extracted_skills: list[str],
        education_entries: list[dict[str, object]],
        experience_entries: list[dict[str, object]],
    ) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO resumes (
                    original_filename,
                    stored_filename,
                    file_path,
                    extracted_text,
                    extracted_skills,
                    education_json,
                    experience_json,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    original_filename,
                    stored_filename,
                    file_path,
                    extracted_text,
                    serialize_skills(extracted_skills),
                    json.dumps(education_entries),
                    json.dumps(experience_entries),
                    utc_now(),
                ),
            )
            return int(cursor.lastrowid)

    def list_resumes(self, resume_id: int | None = None) -> list[dict[str, object]]:
        query = (
            "SELECT id, original_filename, extracted_text, extracted_skills, education_json, experience_json, created_at "
            "FROM resumes"
        )
        params: tuple[object, ...] = ()
        if resume_id is not None:
            query += " WHERE id = ?"
            params = (resume_id,)
        query += " ORDER BY id DESC"

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            {
                "resume_id": row["id"],
                "filename": row["original_filename"],
                "extracted_text": row["extracted_text"],
                "extracted_skills": json.loads(row["extracted_skills"]),
                "education": json.loads(row["education_json"] or "[]"),
                "experience": json.loads(row["experience_json"] or "[]"),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get_resume_payload(self, resume_id: int | None = None) -> dict[str, object] | None:
        rows = self.list_resumes(resume_id)
        return rows[0] if rows else None

    def get_resume_file_record(self, resume_id: int | None = None) -> dict[str, object] | None:
        query = "SELECT id, original_filename, file_path FROM resumes"
        params: tuple[object, ...] = ()
        if resume_id is not None:
            query += " WHERE id = ?"
            params = (resume_id,)
        query += " ORDER BY id DESC LIMIT 1"

        with get_connection() as connection:
            row = connection.execute(query, params).fetchone()

        if row is None:
            return None

        return {
            "resume_id": row["id"],
            "filename": row["original_filename"],
            "file_path": row["file_path"],
        }

    def update_resume_analysis(
        self,
        resume_id: int,
        extracted_skills: list[str],
        education_entries: list[dict[str, object]],
        experience_entries: list[dict[str, object]],
    ) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE resumes
                SET extracted_skills = ?,
                    education_json = ?,
                    experience_json = ?
                WHERE id = ?
                """,
                (
                    serialize_skills(extracted_skills),
                    json.dumps(education_entries),
                    json.dumps(experience_entries),
                    resume_id,
                ),
            )

    def delete_resume(self, resume_id: int) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT file_path FROM resumes WHERE id = ?",
                (resume_id,),
            ).fetchone()
            if row is None:
                return False

            connection.execute("DELETE FROM analyses WHERE resume_id = ?", (resume_id,))
            connection.execute("DELETE FROM job_descriptions WHERE resume_id = ?", (resume_id,))
            connection.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))

        file_path = Path(str(row["file_path"]))
        if file_path.exists():
            file_path.unlink()
        return True
