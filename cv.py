import os
import re
import pandas as pd
from datetime import datetime
from pypdf import PdfReader

# --- CONFIGURATION ---
SOURCE_FOLDER = 'student_uploads'
DATABASE_FILE = 'cv_database.csv'


def initialize_system():
    """Ensures the environment is ready for processing."""
    if not os.path.exists(SOURCE_FOLDER):
        os.makedirs(SOURCE_FOLDER)
        print(f"[*] Created folder: {SOURCE_FOLDER}")

    if not os.path.exists(DATABASE_FILE):
        df = pd.DataFrame(columns=['Student Name', 'Filename', 'Last Updated', 'Email Found', 'Phone Found', 'Status'])
        df.to_csv(DATABASE_FILE, index=False)
        print("[*] Created database file.")


def check_cv_content(filepath):
    """Parses PDF to find errors and missing contact info."""
    results = {"email": "No", "phone": "No", "errors": []}

    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Search for email pattern
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            results["email"] = "Yes"

        # Search for phone pattern (Simple 10+ digit check)
        if re.search(r'\+?\d{10,15}', text):
            results["phone"] = "Yes"

    except Exception as e:
        results["errors"].append(f"Read Error: {str(e)}")

    return results


def sync_cvs():
    initialize_system()
    db = pd.read_csv(DATABASE_FILE)

    files = [f for f in os.listdir(SOURCE_FOLDER) if f.endswith('.pdf')]

    if not files:
        print("[!] No PDF files found in 'student_uploads'. Please add files and run again.")
        return

    updated_data = []

    for filename in files:
        path = os.path.join(SOURCE_FOLDER, filename)
        mod_time = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')

        # Standardize Name (Assuming format: Name_ID.pdf)
        student_name = filename.replace('.pdf', '').replace('_', ' ')

        # Analyze Content
        analysis = check_cv_content(path)

        # Determine Status
        status = "Perfect" if (analysis["email"] == "Yes" and analysis["phone"] == "Yes") else "Missing Info"

        updated_data.append({
            'Student Name': student_name,
            'Filename': filename,
            'Last Updated': mod_time,
            'Email Found': analysis["email"],
            'Phone Found': analysis["phone"],
            'Status': status
        })

    # Save to CSV
    new_db = pd.DataFrame(updated_data)
    new_db.to_csv(DATABASE_FILE, index=False)

    print("-" * 30)
    print(f"SUCCESS: Processed {len(files)} CVs.")
    print(f"Results saved to: {DATABASE_FILE}")
    print("-" * 30)


if __name__ == "__main__":
    sync_cvs()