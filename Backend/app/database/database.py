import sqlite3
from contextlib import contextmanager
from datetime import datetime
from json import dumps
from collections.abc import Generator

from app.core.config import DB_PATH


SKILL_SEED = [
    "Python",
    "Java",
    "JavaScript",
    "C++",
    "SQL",
    "Machine Learning",
    "Data Analysis",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "NLP",
    "React",
    "React.js",
    "Node.js",
    "Express.js",
    "MySQL",
    "MongoDB",
    "Docker",
    "AWS",
    "Git",
    "GitHub",
    'Kubernetes',
]


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                extracted_skills TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        _ensure_column(connection, "resumes", "user_id", "user_id INTEGER")
        _ensure_column(connection, "resumes", "education_json", "education_json TEXT NOT NULL DEFAULT '[]'")
        _ensure_column(connection, "resumes", "experience_json", "experience_json TEXT NOT NULL DEFAULT '[]'")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                user_id INTEGER,
                job_title TEXT NOT NULL DEFAULT '',
                company TEXT NOT NULL DEFAULT '',
                description_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
            """
        )
        _ensure_column(connection, "job_descriptions", "user_id", "user_id INTEGER")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                resume_id INTEGER NOT NULL,
                jd_id INTEGER NOT NULL,
                user_id INTEGER,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (resume_id) REFERENCES resumes (id),
                FOREIGN KEY (jd_id) REFERENCES job_descriptions (id)
            )
            """
        )
        _ensure_column(connection, "analyses", "user_id", "user_id INTEGER")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        _ensure_column(connection, "users", "full_name", "full_name TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "users", "email", "email TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "users", "password_hash", "password_hash TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "users", "hashed_password", "hashed_password TEXT NOT NULL DEFAULT ''")
        _ensure_column(connection, "users", "created_at", "created_at TEXT NOT NULL DEFAULT ''")
        existing_skills = {
            row["name"]
            for row in connection.execute("SELECT name FROM skills").fetchall()
        }
        for skill in SKILL_SEED:
            if skill not in existing_skills:
                connection.execute("INSERT INTO skills (name) VALUES (?)", (skill,))


def _ensure_column(connection: sqlite3.Connection, table_name: str, column_name: str, column_sql: str) -> None:
    column_names = {row[1] for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if column_name not in column_names:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}")


def serialize_skills(skills: list[str]) -> str:
    return dumps(skills)


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")
