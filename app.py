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
# This ensures we are always in the correct folder
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
            pdf_data = f.read()
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')

        # 1. Download/Open Link (Chrome-friendly)
        st.download_button(
            label="📥 Download & View CV (Recommended)",
            data=pdf_data,
            file_name=os.path.basename(file_path),
            mime="application/pdf"
        )

        # 2. Direct Link for Fullscreen
        pdf_url = f"data:application/pdf;base64,{base64_pdf}"
        st.markdown(
            f'<a href="{pdf_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#ff4b4b;color:white;padding:10px;border-radius:5px;text-align:center;">Click Here to View Fullscreen (If blocked below)</div></a>',
            unsafe_allow_html=True)

        # 3. Iframe Viewer
        pdf_display = f'<iframe src="{pdf_url}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading preview: {e}")


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
    * **Full Name:** Letters and spaces only. No numbers or special characters.
    * **Student ID:** Numbers only. Exactly 1 to 10 digits.
    * **File:** Must be a PDF file.
    """)

    with st.form("student_form", clear_on_submit=True):
        st.subheader("Submit Your CV")
        u_name = st.text_input("Enter Full Name").strip()
        u_id = st.text_input("Enter Student ID").strip()
        u_file = st.file_uploader("Upload CV (PDF format)", type=['pdf'])

        if st.form_submit_button("Submit CV"):
            # RE-VALIDATION CHECK
            name_valid = bool(re.match(r'^[a-zA-Z\s]+$', u_name))
            id_valid = u_id.isdigit() and len(u_id) <= 10

            if not u_name or not u_id or not u_file:
                st.error("⚠️ Error: All fields (Name, ID, and File) are required!")

            elif not name_valid:
                st.error("❌ Name Error: Only letters (A-Z) and spaces are allowed. Numbers are forbidden.")

            elif not id_valid:
                st.error("❌ ID Error: ID must be numbers only and no more than 10 digits.")

            else:
                # Process
                file_name = f"{u_id}.pdf"
                full_path = os.path.join(SAVE_FOLDER, file_name)

                with open(full_path, "wb") as f:
                    f.write(u_file.getbuffer())

                with pdfplumber.open(u_file) as pdf:
                    raw_text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

                score, details = perform_detailed_audit(raw_text)
                df = load_data()
                new_row = pd.DataFrame([{
                    "Name": u_name, "ID": u_id, "Score": score,
                    "Audit_Details": details, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
                st.success(f"✅ Success! {u_name}, your CV has been recorded.")

with tab2:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        pw = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Access Denied")
    else:
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

        df_admin = load_data()
        if not df_admin.empty:
            zip_data = create_zip_of_cvs(SAVE_FOLDER)
            st.download_button("📥 Download All CVs (.zip)", zip_data, "CV_Collection.zip")
            st.dataframe(df_admin, use_container_width=True)

            st.divider()
            names = df_admin["Name"].unique().tolist()
            sel_name = st.selectbox("Select Student", names)
            rec = df_admin[df_admin["Name"] == sel_name].iloc[-1]

            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Audit Score", f"{rec['Score']}/100")
                for line in str(rec['Audit_Details']).split(" | "):
                    if "✅" in line:
                        st.success(line)
                    else:
                        st.error(line)

            with col2:
                target = os.path.join(SAVE_FOLDER, f"{rec['ID']}.pdf")
                if os.path.exists(target):
                    display_pdf(target)
                else:
                    st.error("File not found on server.")

            st.divider()
            with st.expander("⚠️ Danger Zone"):
                if st.button("RESET DATABASE"):
                    if os.path.exists(DB_FILE): os.remove(DB_FILE)
                    if os.path.exists(SAVE_FOLDER): shutil.rmtree(SAVE_FOLDER)
                    os.makedirs(SAVE_FOLDER)
                    st.rerun()