from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads" / "resumes"
DB_PATH = DATA_DIR / "resume_analyzer.db"
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPE = "application/pdf"
JWT_SECRET_KEY = "change-this-secret-key-before-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ensure_directories()
