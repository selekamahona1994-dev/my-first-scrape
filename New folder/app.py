import import streamlit as st
import pandas as pd
import os
import pdfplumber
import re
from datetime import datetime

# --- CONFIGURATION ---
DB_FILE = "cv_database.csv"
SAVE_FOLDER = "cv_files"
if not os.path.exists(SAVE_FOLDER): os.makedirs(SAVE_FOLDER)

# --- THE AUDIT ENGINE ---
def run_auto_audit(text):
    t = text.lower()
    checks = {
        "Education": ["education", "degree", "university", "college"],
        "Experience": ["experience", "work", "employment", "internship"],
        "Skills": ["skills", "tools", "technologies", "competencies"]
    }

    results = []
    found_count = 0

    for section, keywords in checks.items():
        if any(key in t for key in keywords):
            results.append(f"✅ {section} section found.")
            found_count += 1
        else:
            results.append(f"❌ {section} section is missing or poorly labeled.")

    # Contact Check
    if "@" in t:
        results.append("✅ Email address detected.")
    else:
        results.append("❌ No email address found.")

    status = "Approved" if found_count >= 2 else "Needs Revision"
    return results, status

# --- UI ---
st.set_page_config(page_title="Class CV Portal", layout="wide")
st.title("🎓 Class CV Collection & Auto-Audit")

# Initialize Database
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=["Name", "ID", "Status", "Timestamp"])

tab1, tab2 = st.tabs(["📤 Student Submission", "📋 Admin Dashboard"])

with tab1:
    with st.form("cv_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        sid = st.text_input("Student ID")
        file = st.file_uploader("Upload CV (PDF)", type=['pdf'])
        submit = st.form_submit_button("Submit CV")

        if submit and name and sid and file:
            path = os.path.join(SAVE_FOLDER, f"{sid}.pdf")
            with open(path, "wb") as f: f.write(file.getbuffer())

            # Extract Text & Audit
            with pdfplumber.open(file) as pdf:
                text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

            audit_notes, final_status = run_auto_audit(text)

            # Save to CSV
            new_row = {"Name": name, "ID": sid, "Status": final_status, "Timestamp": datetime.now()}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)

            st.success(f"CV Submitted! Status: {final_status}")
            for note in audit_notes: st.write(note)

with tab2:
    st.subheader("Database Overview")
    st.dataframe(df, use_container_width=True)