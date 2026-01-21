import pandas as pd
import ollama

# 1. Load the links/snippets
df = pd.read_csv("scholar_summary.csv")

print(f"🧠 Analyzing {len(df)} snippets with DeepSeek-R1 (Light Mode)...")

analysis_results = []

for index, row in df.iterrows():
    print(f"Processing ({index + 1}/{len(df)}): {row['Title'][:50]}")

    prompt = f"""Analyze this paper snippet and identify:
    1. Key Research Gap
    2. Main Methodology
    PAPER: {row['Title']} - {row['Snippet']}"""

    try:
        response = ollama.chat(model='deepseek-r1:8b', messages=[{'role': 'user', 'content': prompt}])
        analysis_results.append(response['message']['content'])
    except:
        analysis_results.append("AI Error")

# 2. Add analysis back to the CSV
df['AI_Analysis'] = analysis_results
df.to_csv("final_gap_analysis.csv", index=False)
print("✅ Completed! View 'final_gap_analysis.csv' for the results.")