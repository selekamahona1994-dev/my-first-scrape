import pandas as pd
import os

# --- CONFIGURATION ---
FILE_NAME = "class_grades.csv"


def calculate_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def initialize_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        return pd.DataFrame(columns=["Student Name", "Subject", "Score", "Grade"])


def main():
    df = initialize_data()
    while True:
        print("\n" + "=" * 30)
        print(" STUDENT MARKS SYSTEM ")
        print("=" * 30)
        print("1. Enter New Marks")
        print("2. View All Student Records")
        print("3. Save and Exit")

        choice = input("\nSelect an option (1-3): ")

        if choice == '1':
            try:
                name = input("Enter Student Name: ").strip()
                subject = input("Enter Subject: ").strip()
                score = float(input("Enter Score (0-100): "))
                if 0 <= score <= 100:
                    grade = calculate_grade(score)
                    new_entry = pd.DataFrame(
                        {"Student Name": [name], "Subject": [subject], "Score": [score], "Grade": [grade]})
                    df = pd.concat([df, new_entry], ignore_index=True)
                    print(f"\n✅ Success: Data for {name} added.")
                else:
                    print("\n❌ Error: Score must be 0-100.")
            except ValueError:
                print("\n❌ Error: Please enter a valid number.")

        elif choice == '2':
            if df.empty:
                print("\n[!] No records found.")
            else:
                print("\n--- Current Gradebook ---")
                print(df.to_string(index=False))

        elif choice == '3':
            df.to_csv(FILE_NAME, index=False)
            print(f"\n💾 Saved to '{FILE_NAME}'. Exiting.")
            break
        else:
            print("\n❌ Invalid choice.")


if __name__ == "__main__":
    main()