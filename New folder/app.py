import streamlit as st
import pandas as pd
import os
import pdfplumber
import base64
import zipfile
import shutil
from io import BytesIO
from datetime import datetime
import re

# --- CONFIG ---
# We use absolute paths to ensure the app finds files regardless of the folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "cv_database.csv")
SAVE_FOLDER = os.path.join(BASE_DIR, "cv_files")
ADMIN_PASSWORD = "admin123"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)


# --- DETECTION ENGINE ---
def perform_detailed_audit(text):
    t = " ".join(text.lower().split())
    criteria = {
        "Personal Profile": ["profile", "summary", "objective", "about me", "career", "biography", "statement"],
        "Personal Details": ["nationality", "date of birth", "gender", "marital status", "id number", "dob", "bio",
                             "residence"],
        "Contact Info": ["email", "phone", "address", "contact", "cell", "telephone", "mobile"],
        "Language Proficiency": ["language", "english", "swahili", "proficiency", "speak"],
        "Academic Qualification": ["academic", "education", "degree", "university", "school", "college", "kcse"],
        "Professional Qualification": ["professional qualification", "certification", "certified", "diploma"],
        "Professional Experience": ["experience", "employment", "work history", "internship", "duties"],
        "Training & Workshops": ["training", "workshop", "seminar", "course"],
        "Technical Literacy": ["computer", "literacy", "software", "ict", "digital", "office", "excel", "word"],
        "Referees": ["referees", "references", "recommendation", "referee"]
    }
    audit_results = {}
    found_count = 0
    for label, keywords in criteria.items():
        is_found = any(key in t for key in keywords)
        audit_results[label] = "✅ Found" if is_found else "❌ Missing"
        if is_found: found_count += 1
    score = int((found_count / len(criteria)) * 100)
    detailed_report = " | ".join([f"{k}: {v}" for k, v in audit_results.items()])
    return score, detailed_report


# --- HELPERS ---
def display_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # Download button as a reliable backup
        with open(file_path, "rb") as f:
            st.download_button(
                label="📄 Open PDF in New Tab / Download",
                data=f,
                file_name=os.path.basename(file_path),
                mime="application/pdf"
            )

        # The PDF Viewer
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")


def create_zip_of_cvs(folder_path):
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".pdf"):
                    z.write(os.path.join(root, file), file)
    return buf.getvalue()


def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Name", "ID", "Score", "Audit_Details", "Timestamp"])


# --- UI SETUP ---
st.set_page_config(page_title="CV Management System", layout="wide")
st.title("🎓 Smart CV Portal")

tab1, tab2 = st.tabs(["📤 Student Submission", "🔒 Admin Dashboard"])

with tab1:
    st.info("""
    ### 📝 Submission Rules
    1. **Full Name:** Use ONLY letters (A-Z). Numbers are not allowed.
    2. **Student ID:** Use ONLY numbers (0-9). Maximum 10 digits.
    3. **File:** Must be a **PDF**.
    """)

    with st.form("student_form", clear_on_submit=True):
        st.subheader("Submit Your CV")
        u_name = st.text_input("Full Name (Letters only)").strip()
        u_id = st.text_input("Student ID (Numbers only, max 10)").strip()
        u_file = st.file_uploader("Upload CV (PDF)", type=['pdf'])

        if st.form_submit_button("Submit CV"):
            # STRICT VALIDATION
            clean_name = u_name.replace(" ", "")

            if not u_name or not u_id or not u_file:
                st.error("⚠️ All fields are required.")

            elif not clean_name.isalpha():
                st.error("❌ Name Error: Only letters are allowed. Please remove numbers or symbols.")

            elif not u_id.isdigit():
                st.error("❌ ID Error: Only numbers are allowed.")

            elif len(u_id) > 10:
                st.error("❌ ID Error: Maximum 10 digits allowed.")

            else:
                # SUCCESS - Process file
                file_filename = f"{u_id}.pdf"
                full_save_path = os.path.join(SAVE_FOLDER, file_filename)

                with open(full_save_path, "wb") as f:
                    f.write(u_file.getbuffer())

                with pdfplumber.open(u_file) as pdf:
                    raw_text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

                score, details = perform_detailed_audit(raw_text)
                df = load_data()
                new_row = pd.DataFrame([{
                    "Name": u_name,
                    "ID": u_id,
                    "Score": score,
                    "Audit_Details": details,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
                st.success(f"✅ Success! CV for {u_name} (ID: {u_id}) has been audited and saved.")

with tab2:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        with st.form("login"):
            pw = st.text_input("Admin Password", type="password")
            if st.form_submit_button("Login"):
                if pw == ADMIN_PASSWORD:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Access Denied")
    else:
        c_head, c_log = st.columns([5, 1])
        c_head.subheader("Admin Audit Dashboard")
        if c_log.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

        df_admin = load_data()
        if not df_admin.empty:
            # Download All Button
            zip_data = create_zip_of_cvs(SAVE_FOLDER)
            st.download_button(label="📥 Download All CVs (.zip)", data=zip_data,
                               file_name=f"CV_Collection.zip", mime="application/zip")

            st.dataframe(df_admin, use_container_width=True)
            st.divider()

            # Viewer Logic
            names = df_admin["Name"].dropna().unique().tolist()
            if names:
                sel_name = st.selectbox("Select Student to Review", options=names)
                # Get the most recent entry for this name
                rec = df_admin[df_admin["Name"] == sel_name].iloc[-1]

                c1, c2 = st.columns([1, 2])
                with c1:
                    st.metric("Audit Score", f"{rec['Score']}/100")
                    st.write("### Audit Breakdown")
                    for line in str(rec['Audit_Details']).split(" | "):
                        if "✅" in line:
                            st.success(line)
                        else:
                            st.error(line)

                with c2:
                    st.write(f"### CV Preview: {sel_name}")
                    target_file = os.path.join(SAVE_FOLDER, f"{rec['ID']}.pdf")
                    if os.path.exists(target_file):
                        display_pdf(target_file)
                    else:
                        st.warning(f"File not found. Looking for: {target_file}")

            # Danger Zone
            st.divider()
            with st.expander("⚠️ Danger Zone (Reset Database)"):
                st.warning("This will permanently delete ALL data.")
                confirm = st.checkbox("Confirm deletion")
                if st.button("DELETE ALL DATA", type="primary"):
                    if confirm:
                        if os.path.exists(DB_FILE): os.remove(DB_FILE)
                        if os.path.exists(SAVE_FOLDER):
                            shutil.rmtree(SAVE_FOLDER)
                        os.makedirs(SAVE_FOLDER)
                        st.success("Everything deleted. App resetting...")
                        st.rerun()

        else:
            st.info("No submissions found yet.")