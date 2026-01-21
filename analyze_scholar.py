import pandas as pd
import ollama
import os

# 1. Load the Scholar data
INPUT_FILE = "scholar_summary.csv"
OUTPUT_FILE = "tanzania_knowledge_analysis.csv"

if not os.path.exists(INPUT_FILE):
    print(f"❌ Could not find {INPUT_FILE}!")
    exit()

df = pd.read_csv(INPUT_FILE)
results = []

print(f"🧠 Analyzing {len(df)} snippets with DeepSeek-R1 (Light Mode)...")

# 2. Loop through snippets
for index, row in df.iterrows():
    print(f"[{index + 1}/{len(df)}] Analyzing: {row['Title'][:50]}...")

    # Simple prompt for the 1.5b model
    prompt = f"""Analyze this research snippet about Tanzania:
    TITLE: {row['Title']}
    SNIPPET: {row['Snippet']}

    Identify:
    1. How communication is used to share knowledge.
    2. A gap (what is missing in their knowledge system?).
    """

    try:
        response = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}])
        analysis = response['message']['content']
    except Exception as e:
        analysis = f"Error: {e}"

    results.append({
        "Title": row['Title'],
        "Link": row['Link'],
        "AI_Analysis": analysis
    })

# 3. Save results
pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
print(f"\n✅ Done! Analysis saved to {OUTPUT_FILE}")