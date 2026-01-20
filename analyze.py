import pandas as pd

# 1. Load the data
df = pd.read_csv('scraped_quotes.csv')

# 2. Count quotes per author
author_counts = df['Author'].value_counts()

print("--- Quote Statistics ---")
print(author_counts)

# 3. Find the most famous author in your list
top_author = author_counts.idxmax()
print(f"\nYour most featured author is: {top_author}")