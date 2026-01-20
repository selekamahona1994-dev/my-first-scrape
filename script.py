import pandas as pd
import os

# --- CONFIGURATION ---
FILE_NAME = "class_grades.csv"


def calculate_grade(score):
    """Determines the letter grade based on a percentage score."""
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
    """Loads existing CSV or creates a new empty DataFrame if file doesn't exist."""
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
            # Data Input Section
            try:
                name = input("Enter Student Name: ").strip()
                subject = input("Enter Subject: ").strip()
                score = float(input("Enter Score (0-100): "))

                if 0 <= score <= 100:
                    grade = calculate_grade(score)

                    # Create a new row
                    new_entry = pd.DataFrame({
                        "Student Name": [name],
                        "Subject": [subject],
                        "Score": [score],
                        "Grade": [grade]
                    })

                    # Add to the main DataFrame
                    df = pd.concat([df, new_entry], ignore_index=True)
                    print(f"\n✅ Success: Data for {name} added.")
                else:
                    print("\n❌ Error: Score must be between 0 and 100.")
            except ValueError:
                print("\n❌ Error: Please enter a valid number for the score.")

        elif choice == '2':
            # Display Section
            if df.empty:
                print("\n[!] No records found yet.")
            else:
                print("\n--- Current Gradebook ---")
                print(df.to_string(index=False))  # index=False makes it look cleaner

        elif choice == '3':
            # Save and Exit Section
            df.to_csv(FILE_NAME, index=False)
            print(f"\n💾 Data saved to '{FILE_NAME}'. Exiting program.")
            break

        else:
            print("\n❌ Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()