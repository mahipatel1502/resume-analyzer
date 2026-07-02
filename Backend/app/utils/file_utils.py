from pathlib import Path


def ensure_pdf_path(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
