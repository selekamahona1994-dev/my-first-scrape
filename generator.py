import pandas as pd
import ollama

# 1. LOAD DATA
try:
    df = pd.read_csv("tanzania_knowledge_analysis.csv")
    knowledge_data = "\n".join(df['AI_Analysis'].tolist())
except Exception as e:
    print(f"❌ Error: Could not find the analysis file. {e}")
    exit()

# 2. THE MASTER PROMPT
# I have enriched this prompt with the SECI Model and Social Constructivism
prompt = f"""
You are a Senior Academic Advisor. Using the literature data provided, write a formal 3-page Thesis Proposal.

TOPIC: Communication as a Source of Knowledge in Tanzania
CONTEXT: Agricultural and Health Information Systems
LITERATURE DATA: {knowledge_data}

REQUIRED SECTIONS:
1. TITLE: Academic, clear, and focused on Tanzania.
2. PROBLEM STATEMENT: Contrast the 'surge in information' with the 'lack of actionable knowledge' in rural Tanzania. Mention language barriers (Kiswahili vs. Jargon).
3. THEORETICAL FRAMEWORK: Explicitly use the SECI Model (Nonaka & Takeuchi) to explain the conversion of Tacit knowledge to Explicit knowledge through communication.
4. RESEARCH QUESTIONS: 
   - How do interpersonal networks facilitate knowledge socialization in Tanzanian villages?
   - To what extent does language jargon hinder the externalization of scientific knowledge?
   - Which communication channels are most effective for 'internalizing' agricultural best practices?
5. METHODOLOGY: Propose a Qualitative Case Study approach using semi-structured interviews in a specific Tanzanian region.
"""

# 3. RUN AI (Using the fast 1.5b model)
print("🚀 Synthesizing your Tanzanian research into a formal proposal...")
response = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}])

# 4. SAVE TO FILE
with open("Tanzania_Knowledge_Proposal.txt", "w", encoding="utf-8") as f:
    f.write(response['message']['content'])

print("\n✨ SUCCESS! Open 'Tanzania_Knowledge_Proposal.txt' to see your draft.")