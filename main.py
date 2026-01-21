import os
import pandas as pd
from pypdf import PdfReader
import ollama

# --- SETTINGS ---
PDF_FOLDER = "papers"
OUTPUT_FILE = "local_research_analysis.csv"
# Using 1.5b to stop your CPU from overheating and speed up the process
MODEL_NAME = "deepseek-r1:1.5b"


def extract_text(pdf_path):
    """Stronger text extraction that handles 'broken' PDF objects."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        # Try to read the first 8 pages (sufficient for gaps)
        pages_to_read = min(len(reader.pages), 8)

        for i in range(pages_to_read):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text += page_text + "\n"

        # Final check if text was actually found
        if len(text.strip()) < 100:
            return "Skip: Scanned image or unreadable formatting."

        return text
    except Exception as e:
        return f"Skip: Error reading file ({str(e)})"


def analyze_with_local_ai(text):
    """Sends text to local DeepSeek-R1 and gets research gaps."""
    # Shorten the prompt and context to make it faster for the CPU
    prompt = f"""Identify the core Methodology and one specific Research Gap in this text.
    Be concise.

    TEXT: {text[:4000]}"""

    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'user', 'content': prompt}
        ])
        return response['message']['content']
    except Exception as e:
        return f"AI Error: {e}"


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"📁 Created '{PDF_FOLDER}' folder. Add PDFs and run again.")
        exit()

    files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

    # Load or create results list
    if os.path.exists(OUTPUT_FILE):
        results = pd.read_csv(OUTPUT_FILE).to_dict('records')
        processed_files = {r['File'] for r in results if "Skip" not in str(r['Analysis'])}
        print(f"⏩ Found existing CSV. Resuming with {len(files) - len(processed_files)} papers left.")
    else:
        results = []
        processed_files = set()

    print(f"🚀 Processing {len(files)} papers...")

    for filename in files:
        if filename in processed_files:
            continue

        print(f"📄 Reading: {filename}...")
        full_path = os.path.join(PDF_FOLDER, filename)

        # 1. Extract and Analyze
        raw_text = extract_text(full_path)

        if "Skip:" in raw_text:
            analysis = raw_text
        else:
            print(f"   🧠 DeepSeek is thinking...")
            analysis = analyze_with_local_ai(raw_text)

        # 2. Update results list
        # If the file was previously skipped, update it; otherwise, add it.
        found = False
        for r in results:
            if r['File'] == filename:
                r['Analysis'] = analysis
                found = True
                break
        if not found:
            results.append({"File": filename, "Analysis": analysis})

        # 3. LIVE SAVE
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        print(f"   💾 Saved progress.")

    print(f"\n✅ FINISHED! Check {OUTPUT_FILE}")