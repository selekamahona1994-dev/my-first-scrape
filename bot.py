import requests
from bs4 import BeautifulSoup
import csv

base_url = "http://quotes.toscrape.com"
current_page = "/page/1/"
all_quotes = []

print("🚀 Starting the Multi-Page Scraper...")

# The 'While' loop keeps going as long as there is a "Next" button
while current_page:
    response = requests.get(base_url + current_page)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract quotes from the current page
    quotes = soup.find_all('div', class_='quote')
    for quote in quotes:
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        all_quotes.append([text, author])

    print(f"✅ Scraped: {base_url + current_page}")

    # Logic to find the "Next" button link
    next_btn = soup.find('li', class_='next')
    if next_btn:
        current_page = next_btn.find('a')['href']
    else:
        current_page = None  # This stops the loop when no "Next" button exists

# Save all 100 quotes to your CSV
with open('scraped_quotes.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Quote', 'Author'])
    writer.writerows(all_quotes)

print(f"\n✨ Done! Total quotes collected: {len(all_quotes)}")