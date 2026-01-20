import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("scraped_quotes.csv")
top_authors = df["Author"].value_counts().head(10)
plt.figure(figsize=(10, 6))
top_authors.plot(kind="bar", color="skyblue", edgecolor="black")
plt.title("Top 10 Most Quoted Authors")
plt.ylabel("Number of Quotes")
plt.tight_layout()
plt.savefig("author_chart.png")
print("✅ Chart saved as author_chart.png!")
