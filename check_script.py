import os
import yaml
import pandas as pd


def analyze_student_cvs(folder_path):
    all_data = []

    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found.")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".yaml"):
            with open(os.path.join(folder_path, filename), 'r') as f:
                data = yaml.safe_load(f)

                # Logic: Calculate a quality score (0-100)
                score = 0
                fields = ['name', 'email', 'skills', 'experience']
                for field in fields:
                    if data.get(field):
                        score += 25

                data['quality_score'] = score
                data['filename'] = filename
                all_data.append(data)

    # Create the organized database
    df = pd.DataFrame(all_data)
    df.to_csv("cv_analytics_report.csv", index=False)
    print("Database updated: cv_analytics_report.csv")
    return df


# Run the analyzer
analyze_student_cvs('submissions')