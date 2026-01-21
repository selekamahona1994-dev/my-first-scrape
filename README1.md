# 🎓 Class CV Manager & Automation Pipeline
**A data-driven solution for standardizing student CVs using Python and GitHub Actions.**

## 📊 Project Overview
This project automates the collection, validation, and standardization of CVs for our class. As a Sustainability and Management professional, I developed this tool to ensure data integrity and quality control across a diverse group of students.

### Key Features:
* **Automated Validation:** Uses GitHub Actions to check submissions for missing fields (Email, Skills, etc.).
* **Centralized Database:** Automatically compiles individual YAML entries into a master `cv_analytics_report.csv`.
* **Quality Scoring:** Assigns a completeness score to help students identify areas for improvement.

---

## 🚀 How Students Submit Their CV
To participate in the class database, please follow these steps:

1.  **Fork** this repository to your own account.
2.  Navigate to the `submissions/` folder.
3.  Create a new file named `yourname_surname.yaml`.
4.  Copy the content from `template.yaml` and enter your professional details.
5.  Submit a **Pull Request**. 

> **Note:** Our automation will instantly review your submission. If you see a ❌, check the "Actions" tab to see what information you missed!

---

## 🛠️ Tech Stack
* **Environment:** Anaconda (Python 3.x)
* **Libraries:** `pandas` (Data Analysis), `PyYAML` (Data Parsing)
* **CI/CD:** GitHub Actions (Automated Quality Assurance)