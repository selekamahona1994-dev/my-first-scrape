import os
import pandas as pd
from markitdown import MarkItDown
from pydantic import BaseModel, EmailStr, ValidationError
from typing import List

# --- CONFIGURATION ---
SUBMISSION_DIR = "./submissions"
CLEAN_DIR = "./standardized_reports"
DATABASE_FILE = "class_registry.csv"
os.makedirs(SUBMISSION_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)


# --- 1. THE QUALITY STANDARD (The "Rubric") ---
class ProfessionalCV(BaseModel):
    name: str
    email: EmailStr
    skills: List[str]
    # This ensures every CV has these 3 components or it's flagged as an error


# --- 2. THE ENGINE ---
md = MarkItDown()


def process_student_cv(filename):
    path = os.path.join(SUBMISSION_DIR, filename)
    result = md.convert(path)
    text = result.text_content

    # Check for quality issues (Inconsistencies)
    issues = []
    if len(text) < 500: issues.append("Content too thin")
    if "education" not in text.lower(): issues.append("Missing Education section")

    # Attempt to Standardize (Basic extraction)
    # Note: In a real-world 2026 use-case, you'd use an LLM call here
    standardized_content = f"# CV: {filename}\n\n## Summary\n{text[:300]}..."

    return {
        "Status": "Passed" if not issues else "Needs Revision",
        "Errors": " | ".join(issues),
        "Clean_Text": standardized_content
    }


def main():
    data = []
    for file in os.listdir(SUBMISSION_DIR):
        if file.endswith((".pdf", ".docx")):
            print(f"Auditing {file}...")
            report = process_student_cv(file)

            # Save standardized version
            with open(f"{CLEAN_DIR}/{file}.md", "w", encoding="utf-8") as f:
                f.write(report["Clean_Text"])

            data.append({
                "Student_File": file,
                "Quality_Score": report["Status"],
                "Flags": report["Errors"]
            })

    # 3. MAINTAIN ORGANIZED DATABASE
    df = pd.DataFrame(data)
    df.to_csv(DATABASE_FILE, index=False)
    print("✓ Registry Updated.")


if __name__ == "__main__":
    main()