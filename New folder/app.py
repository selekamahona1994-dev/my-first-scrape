import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
DB_FILE = "cv_database.csv"
SAVE_FOLDER = "cv_files"
# Expanded columns to include quality notes and error tracking
COLUMNS = ["Student Name", "ID", "Email", "Last Updated", "Status", "Reviewer Notes", "File Path"]

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)


def load_data():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DB_FILE, index=False)
        return df
    df = pd.read_csv(DB_FILE)
    # Ensure all columns exist (Self-healing)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def save_data(df):
    df.to_csv(DB_FILE, index=False)


# --- UI DESIGN ---
st.set_page_config(page_title="Class CV Manager", layout="wide")
st.title("🎓 Class CV Collection & Quality Control")

df = load_data()

tab1, tab2 = st.tabs(["📤 Student Submission", "🔍 Admin Review & Quality Check"])

# --- TAB 1: COLLECTION & UPDATES ---
with tab1:
    st.subheader("Submit or Update Your CV")
    with st.form("cv_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        student_id = st.text_input("Student ID")
        email = st.text_input("Email")
        file = st.file_uploader("Upload CV (PDF)", type=['pdf'])

        if st.form_submit_button("Submit CV"):
            if name and student_id and file:
                file_path = os.path.join(SAVE_FOLDER, f"{student_id}_{name.replace(' ', '_')}.pdf")
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

                # Update existing student or add new
                df['ID'] = df['ID'].astype(str)
                if str(student_id) in df['ID'].values:
                    idx = df.index[df['ID'] == str(student_id)].tolist()[0]
                    df.at[idx, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    df.at[idx, "Status"] = "Updated - Pending Review"
                    st.success(f"Updated CV for {name}.")
                else:
                    new_entry = {
                        "Student Name": name, "ID": str(student_id), "Email": email,
                        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Status": "New Submission", "Reviewer Notes": "", "File Path": file_path
                    }
                    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    st.success(f"Successfully collected CV for {name}.")
                save_data(df)
            else:
                st.error("Missing information. Please check your inputs.")

# --- TAB 2: REVIEW & STANDARDIZATION ---
with tab2:
    st.subheader("Reviewer Dashboard")

    # Overview Table
    st.dataframe(df.drop(columns=["File Path"]), use_container_width=True)

    st.divider()

    if not df.empty:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Select Student to Audit")
            target = st.selectbox("Choose Student", df['Student Name'].unique())
            current_row = df[df['Student Name'] == target].iloc[0]

            st.info(f"**Current Status:** {current_row['Status']}")

            # Standardization Checklist
            st.markdown("### Standardization Checklist")
            c1 = st.checkbox("Format is Standardized (Font, Margins)")
            c2 = st.checkbox("No Spelling/Grammar Errors")
            c3 = st.checkbox("Contact Info is Correct")
            c4 = st.checkbox("Reverse Chronological Order")

        with col2:
            st.markdown("### Reviewer Feedback")
            new_status = st.selectbox("Update Status", ["Pending Review", "Needs Revision", "Standardized & Approved"])
            notes = st.text_area("Feedback for Student (Errors/Inconsistencies)", value=current_row['Reviewer Notes'])

            if st.button("Save Audit Results"):
                idx = df.index[df['Student Name'] == target].tolist()[0]
                df.at[idx, "Status"] = new_status
                df.at[idx, "Reviewer Notes"] = notes
                save_data(df)
                st.success(f"Audit for {target} saved!")
                st.rerun()