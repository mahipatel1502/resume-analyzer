from app.database.database import get_connection, utc_now


class AuthRepository:
    def create_user(self, full_name: str, email: str, password_hash: str) -> dict[str, object]:
        password_columns = self._get_password_columns()
        insert_columns = ["full_name", "email", "created_at", *password_columns]
        placeholders = ", ".join(["?"] * len(insert_columns))
        values: list[object] = [full_name, email, utc_now()]
        values.extend([password_hash for _ in password_columns])

        with get_connection() as connection:
            cursor = connection.execute(
                f"""
                INSERT INTO users ({", ".join(insert_columns)})
                VALUES ({placeholders})
                """,
                values,
            )
            user_id = int(cursor.lastrowid)

        return self.get_user_by_id(user_id) or {}

    def get_user_by_email(self, email: str) -> dict[str, object] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, full_name, email, COALESCE(password_hash, hashed_password) AS password_hash, created_at
                FROM users
                WHERE email = ?
                """,
                (email.casefold(),),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    def get_user_by_id(self, user_id: int) -> dict[str, object] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, full_name, email, COALESCE(password_hash, hashed_password) AS password_hash, created_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_user(row)

    def _row_to_user(self, row: object) -> dict[str, object]:
        return {
            "id": int(row["id"]),
            "full_name": str(row["full_name"] or ""),
            "email": str(row["email"]),
            "password_hash": str(row["password_hash"]),
            "created_at": str(row["created_at"]),
        }

    def _get_password_columns(self) -> list[str]:
        with get_connection() as connection:
            rows = connection.execute("PRAGMA table_info(users)").fetchall()

        column_names = {str(row[1]) for row in rows}
        password_columns: list[str] = []
        if "password_hash" in column_names:
            password_columns.append("password_hash")
        if "hashed_password" in column_names:
            password_columns.append("hashed_password")
        return password_columns or ["password_hash"]