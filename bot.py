import requests
from bs4 import BeautifulSoup
import csv


def scrape_quotes():
    # 1. The URL we want to scrape
    url = "http://quotes.toscrape.com"

    # 2. Ask the website for the data
    print(f"Connecting to {url}...")
    response = requests.get(url)

    if response.status_code == 200:
        # 3. Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find_all('div', class_='quote')

        # 4. Create a CSV file to save the data
        with open('scraped_quotes.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Quote", "Author"])  # Headers

            print("Scraping and saving data...")
            for quote in quotes:
                text = quote.find('span', class_='text').text
                author = quote.find('small', class_='author').text
                writer.writerow([text, author])

        print("Success! Data saved to 'scraped_quotes.csv'.")
    else:
        print(f"Failed to reach website. Error code: {response.status_code}")


if __name__ == "__main__":
    scrape_quotes()