import pandas as pd
import ollama

# 1. Load your analyzed data
try:
    df = pd.read_csv("local_research_analysis.csv")
    # Remove any rows where the AI skipped the paper
    df = df[~df['Analysis'].str.contains("Skip:", na=False)]
except Exception as e:
    print(f"❌ Could not find or read the CSV: {e}")
    exit()

print(f"📄 Synthesizing {len(df)} analyzed papers into a proposal...")

# 2. Prepare the prompt for the "Master Synthesis"
# We give the AI the top 10 most relevant gaps found in your CSV
gaps_summary = "\n".join(df['Analysis'].head(10).tolist())

master_prompt = f"""
You are a senior PhD supervisor. Based on the following research gaps found in recent literature, 
write a structured Thesis Proposal Draft.

TOP TOPIC: Internal Communication between South Africa and India
GAPS FOUND IN LITERATURE:
{gaps_summary}

PROPOSAL STRUCTURE:
1. Proposed Title (Academic and catchy)
2. Problem Statement (Why is this research urgent?)
3. Research Questions (3 specific questions based on the gaps)
4. Proposed Methodology (How should the student solve this?)
"""

# 3. Generate the Thesis
print("🧠 DeepSeek is drafting your proposal (this takes 2-3 minutes)...")
response = ollama.chat(model='deepseek-r1:1.5b', messages=[
    {'role': 'user', 'content': master_prompt}
])

# 4. Save to a Text File
with open("FINAL_THESIS_PROPOSAL.txt", "w", encoding="utf-8") as f:
    f.write(response['message']['content'])

print("\n✨ SUCCESS! Your draft is ready: 'FINAL_THESIS_PROPOSAL.txt'")