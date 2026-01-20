import requests
from bs4 import BeautifulSoup
import csv

base_url = "http://quotes.toscrape.com"
current_page = "/page/1/"
all_quotes = []

print("Starting the full-site crawl...")

while current_page:
    response = requests.get(base_url + current_page)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract quotes
    quotes = soup.find_all('div', class_='quote')
    for q in quotes:
        text = q.find('span', class_='text').text
        author = q.find('small', class_='author').text
        all_quotes.append([text, author])

    print(f"Scraped: {current_page}")

    # Check for the 'Next' button
    next_btn = soup.find('li', class_='next')
    if next_btn:
        current_page = next_btn.find('a')['href']
    else:
        current_page = None  # This stops the loop

# Save all 100 quotes
with open('scraped_quotes.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Quote', 'Author'])
    writer.writerows(all_quotes)

print(f"Done! Collected {len(all_quotes)} quotes.")