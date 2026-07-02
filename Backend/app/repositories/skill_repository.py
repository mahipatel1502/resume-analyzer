from app.database.database import get_connection


class SkillRepository:
    def list_skills(self) -> list[str]:
        with get_connection() as connection:
            rows = connection.execute("SELECT name FROM skills ORDER BY name ASC").fetchall()
        return [row["name"] for row in rows]
