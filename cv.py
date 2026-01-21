import os
import re
import pandas as pd
from datetime import datetime
from pypdf import PdfReader

SOURCE_FOLDER = 'student_uploads'
DATABASE_FILE = 'cv_database.csv'


def clean_name(filename):
    """Standardizes the student name from the filename."""
    name = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
    return name.title()


def analyze_cv(filepath):
    """Checks for quality, errors, and consistency."""
    report = {"email": "Missing", "phone": "Missing", "word_count": 0, "issues": []}
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        report["word_count"] = len(text.split())

        # Check for Errors/Inconsistencies
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            report["email"] = "Found"
        if re.search(r'\+?\d{10,15}', text):
            report["phone"] = "Found"

        # Quality Issue: Too short
        if report["word_count"] < 100:
            report["issues"].append("Content too short")

    except Exception as e:
        report["issues"].append(f"Unreadable file: {str(e)}")
    return report


def sync_and_standardize():
    if not os.path.exists(SOURCE_FOLDER): os.makedirs(SOURCE_FOLDER)

    files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.pdf')]
    updated_data = []

    for filename in files:
        old_path = os.path.join(SOURCE_FOLDER, filename)

        # --- 1. STANDARDIZATION (Renaming) ---
        student_name = clean_name(filename)
        standard_filename = f"CV_{student_name.replace(' ', '_')}.pdf"
        new_path = os.path.join(SOURCE_FOLDER, standard_filename)

        if old_path != new_path:
            os.rename(old_path, new_path)

        # --- 2. REVIEW & QUALITY CHECK ---
        analysis = analyze_cv(new_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(new_path)).strftime('%Y-%m-%d %H:%M')

        updated_data.append({
            'Student Name': student_name,
            'Last Updated': mod_time,
            'Email': analysis["email"],
            'Phone': analysis["phone"],
            'Word Count': analysis["word_count"],
            'Quality Issues': ", ".join(analysis["issues"]) if analysis["issues"] else "None"
        })

    pd.DataFrame(updated_data).to_csv(DATABASE_FILE, index=False)
    print(f"--- Processed {len(files)} CVs. Database updated. ---")


if __name__ == "__main__":
    sync_and_standardize()