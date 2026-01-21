import streamlit as st
import pandas as pd
import os
import pdfplumber
from google import genai
from datetime import datetime

# --- AI CONFIGURATION ---
# This looks for the key in your .streamlit/secrets.toml file
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key not found. Please check your .streamlit/secrets.toml file.")
    st.stop()

# --- FILE PATHS ---
DB_FILE = "cv_database.csv"
SAVE_FOLDER = "cv_files"
if not os.path.exists(SAVE_FOLDER): os.makedirs(SAVE_FOLDER)


def load_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=["Name", "ID", "Email", "Status", "AI_Feedback", "Timestamp"])
    return pd.read_csv(DB_FILE)


# --- APP INTERFACE ---
st.set_page_config(page_title="Class CV Portal", layout="wide")
st.title("🎓 Smart CV Portal: Collection & AI Audit")

df = load_data()
tab1, tab2 = st.tabs(["📤 Student Upload", "📋 Admin Dashboard"])

with tab1:
    st.markdown("### Upload your CV for Automatic AI Review")
    with st.form("cv_upload", clear_on_submit=True):
        u_name = st.text_input("Full Name")
        u_id = st.text_input("Student ID")
        u_email = st.text_input("Email")
        u_file = st.file_uploader("Upload PDF CV", type=['pdf'])
        submit = st.form_submit_button("Submit & Scan for Mistakes")

        if submit and u_file:
            path = os.path.join(SAVE_FOLDER, f"{u_id}.pdf")
            with open(path, "wb") as f:
                f.write(u_file.getbuffer())

            with st.spinner("AI is auditing your CV..."):
                try:
                    # 1. Extract Text from PDF
                    with pdfplumber.open(path) as pdf:
                        cv_text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

                    # 2. Get AI Feedback using the new library
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"Analyze this CV for: 1. Missing sections 2. Spelling errors 3. Tone. CV TEXT: {cv_text}"
                    )
                    feedback = response.text
                except Exception as e:
                    feedback = f"Processing Error: {str(e)}"

            # Update Database
            new_entry = {
                "Name": u_name, "ID": u_id, "Email": u_email,
                "Status": "AI Audited", "AI_Feedback": feedback,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)

            st.success("Submission Successful!")
            st.info(f"**AI Audit Results:**\n\n{feedback}")

with tab2:
    st.subheader("Class CV Database")
    st.dataframe(df, use_container_width=True)