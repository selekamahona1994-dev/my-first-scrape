import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load your API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. LOAD THE DATA (This defines 'df')
try:
    df = pd.read_csv("research_analysis_results.csv")
    print("✅ CSV data loaded successfully.")
except FileNotFoundError:
    print("❌ Error: 'research_analysis_results.csv' not found. Run main.py first!")
    exit()

# 3. COMBINE THE ANALYSES
# We take the text from the 'Analysis' column to give to the AI
summary_of_gaps = " ".join(df['Analysis'].astype(str))

print("Generating your Research Proposal... please wait.")

# 4. GENERATE THE PROPOSAL
try:
    proposal_response = client.chat.completions.create(
        model="gpt-4o", # Stronger model for writing
        messages=[
            {"role": "system", "content": "You are a PhD supervisor and expert academic writer."},
            {"role": "user", "content": f"Based on these research paper analyses, write a professional Research Problem Statement and suggest a Thesis Title. Focus on a gap that hasn't been filled. DATA: {summary_of_gaps[:15000]}"}
        ]
    )

    # 5. SAVE TO A TEXT FILE
    with open("RESEARCH_PROPOSAL_DRAFT.txt", "w", encoding="utf-8") as f:
        f.write(proposal_response.choices[0].message.content)

    print("🚀 SUCCESS! Your proposal is saved in 'RESEARCH_PROPOSAL_DRAFT.txt'")

except Exception as e:
    print(f"❌ AI Error: {e}")