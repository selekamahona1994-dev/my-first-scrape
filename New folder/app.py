import streamlit as st
import pandas as pd
import os
import pdfplumber
import base64
import zipfile
import shutil
from io import BytesIO
from datetime import datetime

# --- CONFIG ---
DB_FILE = "cv_database.csv"
SAVE_FOLDER = "cv_files"
ADMIN_PASSWORD = "admin123"

if not os.path.exists(SAVE_FOLDER): os.makedirs(SAVE_FOLDER)


# --- DETECTION ENGINE ---
def perform_detailed_audit(text):
    t = " ".join(text.lower().split())
    criteria = {
        "Personal Profile": ["profile", "summary", "objective", "about me", "career", "biography", "statement"],
        "Personal Details": ["nationality", "date of birth", "gender", "marital status", "id number", "dob", "bio",
                             "residence", "status"],
        "Contact Info": ["email", "phone", "address", "contact", "cell", "telephone", "mobile", "p.o box", "tel"],
        "Language Proficiency": ["language", "english", "swahili", "proficiency", "speak", "linguistic", "tongue"],
        "Academic Qualification": ["academic", "education", "degree", "university", "school", "institution", "college",
                                   "kcse", "studies"],
        "Professional Qualification": ["professional qualification", "certification", "certified", "accreditation",
                                       "diploma", "member of", "registration"],
        "Professional Experience": ["experience", "employment", "work history", "career", "professional background",
                                    "internship", "duties", "responsibilities"],
        "Training & Workshops": ["training", "workshop", "seminar", "course", "participation", "conference"],
        "Technical & Computer Literacy": ["computer", "literacy", "software", "ict", "digital", "packages", "office",
                                          "excel", "word", "it skills"],
        "Referees": ["referees", "references", "recommendation", "referee", "persons"]
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
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    with open(file_path, "rb") as f:
        st.download_button(
            label="📄 Open PDF in New Tab / Download",
            data=f,
            file_name=os.path.basename(file_path),
            mime="application/pdf"
        )

    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def create_zip_of_cvs(folder_path):
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".pdf"):
                    z.write(os.path.join(root, file), file)
    return buf.getvalue()


def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Name", "ID", "Score", "Audit_Details", "Timestamp"])


# --- UI SETUP ---
st.set_page_config(page_title="CV Management System", layout="wide")
st.title("🎓 Smart CV Portal")

tab1, tab2 = st.tabs(["📤 Student Submission", "🔒 Admin Dashboard"])

with tab1:
    st.info("""
    ### 📝 Submission Instructions
    1. **Full Name:** Use letters only (no numbers).
    2. **Student ID:** Use numbers only (max 10 digits).
    3. **Format:** Upload your CV in **PDF format**.
    """)

    st.divider()

    with st.form("student_form", clear_on_submit=True):
        st.subheader("Submit Your CV")
        u_name = st.text_input("Full Name (Letters only)")
        u_id = st.text_input("Student ID (Numbers only, max 10)")
        u_file = st.file_uploader("Upload CV (PDF)", type=['pdf'])

        if st.form_submit_button("Submit CV"):
            # 1. Check if empty
            if not (u_name and u_id and u_file):
                st.error("⚠️ Please fill all fields and upload your PDF.")

            # 2. Validate Name (No numbers allowed)
            elif not u_name.replace(" ", "").isalpha():
                st.error("❌ Invalid Name: Please use letters only (no numbers or symbols).")

            # 3. Validate ID (Only numbers and max 10 digits)
            elif not (u_id.isdigit() and len(u_id) <= 10):
                st.error("❌ Invalid ID: Please enter numbers only (maximum 10 digits).")

            else:
                # All checks passed - Proceed to save
                path = os.path.join(SAVE_FOLDER, f"{u_id}.pdf")
                with open(path, "wb") as f:
                    f.write(u_file.getbuffer())

                with pdfplumber.open(u_file) as pdf:
                    raw_text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

                score, details = perform_detailed_audit(raw_text)
                df = load_data()
                new_row = pd.DataFrame([{"Name": u_name, "ID": u_id, "Score": score, "Audit_Details": details,
                                         "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
                st.success(f"✅ CV for {u_name} received successfully!")

with tab2:
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
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
            zip_data = create_zip_of_cvs(SAVE_FOLDER)
            st.download_button(label="📥 Download All CVs (.zip)", data=zip_data,
                               file_name=f"CV_Collection_{datetime.now().strftime('%Y%m%d')}.zip",
                               mime="application/zip")

            st.dataframe(df_admin, use_container_width=True)
            st.divider()

            names = df_admin["Name"].dropna().unique().tolist()
            if names:
                sel = st.selectbox("Detailed Auditor View", options=names)
                rec = df_admin[df_admin["Name"] == sel].iloc[-1]
                c1, c2 = st.columns([1, 1.5])
                with c1:
                    st.metric("Audit Score", f"{rec['Score']}/100")
                    for line in str(rec['Audit_Details']).split(" | "):
                        if "✅" in line:
                            st.success(line)
                        else:
                            st.error(line)
                with c2:
                    st.subheader("CV Preview")
                    f_path = os.path.join(SAVE_FOLDER, f"{rec['ID']}.pdf")
                    if os.path.exists(f_path):
                        display_pdf(f_path)
                    else:
                        st.warning(f"File not found: {rec['ID']}.pdf")

            st.divider()
            with st.expander("⚠️ Danger Zone (Reset Database)"):
                st.warning("This will permanently delete all student records and PDF files.")
                confirm = st.checkbox("I confirm I want to delete everything.")
                if st.button("DELETE ALL DATA", type="primary"):
                    if confirm:
                        if os.path.exists(DB_FILE): os.remove(DB_FILE)
                        shutil.rmtree(SAVE_FOLDER)
                        os.makedirs(SAVE_FOLDER)
                        st.success("All records and files have been deleted.")
                        st.rerun()
                    else:
                        st.error("Please check the confirmation box first.")
        else:
            st.info("No submissions found.")