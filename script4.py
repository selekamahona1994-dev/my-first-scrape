import pandas as pd
import os


class SchoolResultSystem:
    def __init__(self, filename="Student_Marks_Template.xlsx"):
        self.filename = filename
        # Common subjects found in the document: HIS, GEO, ECO, BAM, ENG, KIS, G/S [cite: 1, 3]
        self.subjects = ['HIS', 'GEO', 'ECO', 'BAM', 'ENG', 'KIS', 'GS']

    def create_template(self):
        """Generates the User/Student document entry part."""
        columns = ['CNO', 'SEX'] + self.subjects
        # Example row for user guidance
        df = pd.DataFrame(columns=columns)
        df.to_excel(self.filename, index=False)
        print(f"Template created: {self.filename}. Users can now enter data here.")

    def calculate_grade(self, score):
        """Grading logic based on NECTA standards observed in the file."""
        try:
            score = float(score)
            if score >= 80: return ('A', 1)
            if score >= 70: return ('B', 2)
            if score >= 60: return ('C', 3)
            if score >= 50: return ('D', 4)
            if score >= 40: return ('E', 5)
            if score >= 35: return ('S', 6)
            return ('F', 7)
        except:
            return ('F', 7)

    def process_results(self):
        """Administration part: Generates the formula-based results."""
        if not os.path.exists(self.filename):
            print("Error: Template file not found.")
            return

        df = pd.read_excel(self.filename)
        results = []

        for index, row in df.iterrows():
            subject_details = []
            points = []

            for sub in self.subjects:
                score = row[sub]
                grade, point = self.calculate_grade(score)
                subject_details.append(f"{sub} {score}-{grade}")
                # Aggregate usually excludes G/S and BAM depending on combination 
                if sub not in ['GS', 'BAM']:
                    points.append(point)

            # Calculate Aggregate (Sum of best 3 for Form Six)
            points.sort()
            aggt = sum(points[:3])

            # Division Logic [cite: 2]
            if aggt <= 9:
                div = 'I'
            elif aggt <= 12:
                div = 'II'
            elif aggt <= 17:
                div = 'III'
            elif aggt <= 19:
                div = 'IV'
            else:
                div = 'FAIL'

            results.append({
                'CNO': row['CNO'],
                'SEX': row['SEX'],
                'AGGT': aggt,
                'DIV': div,
                'DETAILED SUBJECTS': ", ".join(subject_details)
            })

        final_df = pd.DataFrame(results)
        final_df.to_excel("Final_Mock_Results_Summary.xlsx", index=False)
        print("Final Results Summary generated: Final_Mock_Results_Summary.xlsx")


# --- Execution ---
system = SchoolResultSystem()
# 1. First, the administrator runs this to give the template to users
system.create_template()

# 2. After users fill the 'Student_Marks_Template.xlsx', run this to get the summary
# system.process_results()