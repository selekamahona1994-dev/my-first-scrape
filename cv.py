import os
import re
import pandas as pd
from datetime import datetime
from pypdf import PdfReader

# --- CONFIGURATION ---
SOURCE_FOLDER = 'student_uploads'
DATABASE_FILE = 'cv_database.csv'


def clean_student_name(filename):
    """
    Cleans up filenames to extract only the student's name.
    Removes 'CV', 'Resume', dates, and symbols.
    """
    # Remove extension and lowercase
    name = filename.lower().replace('.pdf', '')
    # Remove common words that clutter the name
    name = name.replace('cv', '').replace('resume', '').replace('2026', '').replace('2025', '')
    # Remove non-alphabet characters
    name = re.sub(r'[^a-zA-Z\s]', ' ', name)
    # Remove extra whitespace and capitalize
    name = ' '.join(name.split()).title()
    return name if name else "Unknown_Student"


def analyze_cv_content(filepath):
    """Parses PDF to find errors and quality issues."""
    report = {"email": "Missing", "phone": "Missing", "word_count": 0, "issues": []}
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        report["word_count"] = len(text.split())

        # Email Check
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            report["email"] = "Found"

        # Phone Check (standard 10+ digits)
        if re.search(r'\+?\d{10,15}', text):
            report["phone"] = "Found"

        # Quality Checks
        if report["word_count"] < 100:
            report["issues"].append("Content too short (Possible error)")

    except Exception as e:
        report["issues"].append(f"File Error: {str(e)}")

    return report


def run_manager():
    if not os.path.exists(SOURCE_FOLDER):
        os.makedirs(SOURCE_FOLDER)

    files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.pdf')]
    if not files:
        print("[!] No CVs found to process.")
        return

    db_records = []
    issues_found = []

    for filename in files:
        old_path = os.path.join(SOURCE_FOLDER, filename)

        # 1. STANDARDIZATION
        student_name = clean_student_name(filename)
        standard_filename = f"CV_{student_name.replace(' ', '_')}.pdf"
        new_path = os.path.join(SOURCE_FOLDER, standard_filename)

        # Rename the physical file
        if old_path != new_path:
            # Check if target exists to avoid errors
            if os.path.exists(new_path): os.remove(new_path)
            os.rename(old_path, new_path)

        # 2. ANALYSIS
        analysis = analyze_cv_content(new_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(new_path)).strftime('%Y-%m-%d %H:%M')

        # 3. DATABASE RECORD
        record = {
            'Student Name': student_name,
            'Filename': standard_filename,
            'Last Updated': mod_time,
            'Email': analysis["email"],
            'Phone': analysis["phone"],
            'Words': analysis["word_count"],
            'Status': "Review Required" if analysis["issues"] or analysis["email"] == "Missing" else "Verified"
        }
        db_records.append(record)

        if record['Status'] == "Review Required":
            issues_found.append(f"- {student_name}: {', '.join(analysis['issues']) or 'Missing Contact Info'}")

    # Save Database
    pd.DataFrame(db_records).to_csv(DATABASE_FILE, index=False)

    # 4. PRINT SUMMARY REPORT
    print("\n" + "=" * 40)
    print(" CV MANAGEMENT REPORT ")
    print("=" * 40)
    print(f"Total CVs Processed: {len(db_records)}")
    print(f"Database Updated:    {DATABASE_FILE}")

    if issues_found:
        print("\n[!] STUDENTS REQUIRING CORRECTIONS:")
        for issue in issues_found:
            print(issue)
    else:
        print("\n[+] All CVs pass basic quality checks!")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    run_manager()