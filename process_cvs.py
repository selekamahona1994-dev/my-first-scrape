import os
import pandas as pd
from markitdown import MarkItDown
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


# 1. Define the Standard Format (Quality Guardrails)
class StudentCV(BaseModel):
    name: str
    email: EmailStr
    phone: str
    skills: List[str]
    experience_years: int = Field(ge=0, description="Years of experience")
    missing_fields: List[str] = []


# 2. Initialize Tools
md = MarkItDown()
SUBMISSION_DIR = "./submissions"
DATABASE_FILE = "cv_database.csv"


def analyze_cv(file_path):
    # Convert PDF/Docx to readable Markdown
    result = md.convert(file_path)
    text = result.text_content

    # SIMPLE LOGIC: In a real 2026 setup, you would pass 'text' to
    # an LLM API here to extract structured JSON.
    # For now, we simulate basic quality checks.
    quality_report = {
        "name": "Extracted Name",  # Placeholder
        "email": "student@example.com" if "@" in text else None,
        "phone": "Found" if any(char.isdigit() for char in text) else None,
        "errors": []
    }

    if not quality_report["email"]:
        quality_report["errors"].append("Missing Email")

    return quality_report


def main():
    records = []
    for filename in os.listdir(SUBMISSION_DIR):
        if filename.endswith((".pdf", ".docx")):
            path = os.path.join(SUBMISSION_DIR, filename)
            print(f"Processing: {filename}...")
            report = analyze_cv(path)
            records.append({
                "Student": filename,
                "Status": "Error" if report["errors"] else "Standardized",
                "Issues": ", ".join(report["errors"]),
                "LastUpdated": pd.Timestamp.now()
            })

    # Save to Database
    df = pd.DataFrame(records)
    df.to_csv(DATABASE_FILE, index=False)
    print("Database Updated.")


if __name__ == "__main__":
    main()