from pathlib import Path

import pdfplumber


class PDFService:
    def extract_text(self, file_path: Path) -> str:
        extracted_pages: list[str] = []
        with pdfplumber.open(str(file_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_pages.append(text)
        return "\n".join(extracted_pages).strip()
