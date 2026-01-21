import arxiv
import os
import ssl
import urllib.request

# --- FIX FOR SSL ERROR ---
ssl._create_default_https_context = ssl._create_unverified_context
# -------------------------

# 1. User Input
topic = input("Enter your research topic: ")
num_papers = int(input("How many papers do you want to find? "))

# 2. Setup Folder
if not os.path.exists("papers"):
    os.makedirs("papers")

# 3. Search arXiv (Using the new Client method to avoid warnings)
client = arxiv.Client()
search = arxiv.Search(
    query=topic,
    max_results=num_papers,
    sort_by=arxiv.SortCriterion.Relevance
)

# 4. Download Everything
print(f"🔎 Searching for '{topic}'...")
count = 0
for result in client.results(search):
    count += 1
    # Clean title for filename (removes invalid characters)
    clean_title = "".join(x for x in result.title if x.isalnum() or x in " -_")[:50]
    filename = f"{clean_title}.pdf"

    print(f"[{count}/{num_papers}] Downloading: {result.title}")

    try:
        result.download_pdf(dirpath="papers", filename=filename)
    except Exception as e:
        print(f"⚠️ Could not download {result.title}: {e}")

print(f"\n✅ DONE! {count} papers are now in your 'papers' folder.")