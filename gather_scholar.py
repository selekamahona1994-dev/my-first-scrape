from scholarly import scholarly
import pandas as pd

# 1. SETTINGS
topic = input("Enter your Research Topic: ")
num_to_find = int(input("How many papers to find (e.g. 50)? "))

results = []
print(f"🔎 Searching Google Scholar for: {topic}...")

# 2. SEARCH
search_query = scholarly.search_pubs(topic)

for i in range(num_to_find):
    try:
        paper = next(search_query)
        # Extract only what we need
        data = {
            "Title": paper['bib'].get('title', 'N/A'),
            "Year": paper['bib'].get('pub_year', 'N/A'),
            "Link": paper.get('pub_url', 'No Link'),
            "Snippet": paper['bib'].get('abstract', 'No abstract available')
        }
        results.append(data)
        print(f"[{i+1}/{num_to_find}] Found: {data['Title'][:60]}...")
    except StopIteration:
        break
    except Exception as e:
        print(f"⚠️ Skipping a result due to error.")

# 3. SAVE
df = pd.DataFrame(results)
df.to_csv("scholar_summary.csv", index=False)
print("\n✅ DONE! Links and snippets saved to 'scholar_summary.csv'")