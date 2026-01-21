import streamlit as st
import pandas as pd
import os
import pdfplumber
import google.generativeai as genai
from datetime import datetime

# --- IMPORTANT: SECURE YOUR API KEY ---
# In Streamlit Cloud, you will put this in "Secrets".
# For local testing, replace the text below with your key.
AI_KEY = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else "YOUR_GEMINI_KEY_HERE"
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIG ---
DB_FILE = "cv_database.csv"
SAVE_FOLDER = "cv_files"
if not os.path.exists(SAVE_FOLDER): os.makedirs(SAVE_FOLDER)


def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame(columns=["Name", "ID", "Status", "AI_Review"])
    return pd.read_csv(DB_FILE)


# --- THE AI BRAIN ---
def analyze_cv(file_path):
    # 1. Read PDF
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
    except:
        return "Error: Could not read PDF file."

    # 2. Ask AI to find mistakes
    prompt = f"""
    Analyze this student CV text for a class project. 
    1. Identify missing sections (e.g., Skills, Contact, Education).
    2. List spelling or grammar mistakes.
    3. Suggest one way to improve professional tone.
    Keep it brief and use bullet points.

    CV TEXT: {text}
    """
    response = model.generate_content(prompt)
    return response.text


# --- UI ---
st.title("🎓 Smart CV Class Portal")
df = load_data()

tab1, tab2 = st.tabs(["📤 Upload & AI Audit", "📋 Admin View"])

with tab1:
    with st.form("upload_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        sid = st.text_input("Student ID")
        file = st.file_uploader("Upload your CV (PDF)", type=['pdf'])
        if st.form_submit_button("Submit & Run AI Audit"):
            if name and sid and file:
                path = os.path.join(SAVE_FOLDER, f"{sid}.pdf")
                with open(path, "wb") as f: f.write(file.getbuffer())

                # Run Automatic AI Check
                with st.spinner("AI is checking for mistakes..."):
                    feedback = analyze_cv(path)

                # Save to database
                new_data = {"Name": name, "ID": sid, "Status": "AI Audited", "AI_Review": feedback}
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)

                st.success("CV Received!")
                st.subheader("🤖 AI Auditor Feedback:")
                st.info(feedback)

with tab2:
    st.dataframe(df, use_container_width=True)