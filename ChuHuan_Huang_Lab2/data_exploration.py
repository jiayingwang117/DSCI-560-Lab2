import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv
import fitz 

# 1. CSV or Excel
# retrieve data of AAPL stock
aapl = yf.Ticker("AAPL")
oneyear_data = aapl.history(period = "1y")  

# save it to CSV
oneyear_data.to_csv("aapl_stock_data.csv")
print(f"\nstock data saved")

#show few rows of the data 
data = pd.read_csv("aapl_stock_data.csv")
print("\nPrint first 10 rows:")
print(data.head(10))
print("\nDataset size:", data.shape)
print("\nMissing data")
print(data.isnull().sum())
print("\n")

# 2. ASCII Texts like Forum Postings and HTML
# retrieve news data of AAPL stock
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}

# Retrieve news data for AAPL stock
search = "AAPL"
template = 'https://news.search.yahoo.com/search?p={}'
url = template.format(search)

response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.find_all('div', 'NewsArticle')

    articles = []
    for card in cards:
        headline = card.find('h4', 's-title').text if card.find('h4', 's-title') else None
        source = card.find("span", 's-source').text if card.find("span", 's-source') else None
        raw_link = card.find('a').get('href') if card.find('a') else None
        clean_link = None
        if raw_link:
            unquoted_link = requests.utils.unquote(raw_link)
            pattern = re.compile(r'RU=(.+)\/RK')
            match = re.search(pattern, unquoted_link)
            clean_link = match.group(1) if match else None

        if headline and source and clean_link:
            articles.append((headline, source, clean_link))

    # Save as CSV
    with open('aapl_news_data.csv', 'w', newline = '', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Headline', 'Source', 'Link'])
        writer.writerows(articles)

    news_df = pd.DataFrame(articles, columns = ['Headline', 'Source', 'Link'])
    news_df.to_csv("aapl_news_data.csv", index = False)
    
    # Analyzing the data
    print("\nPrint first 10 rows:")
    print(news_df.head(10))
    print("\nDataset size:", news_df.shape)
    print("\nMissing data")
    print(news_df.isnull().sum())
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

# 3. PDF and Word Documents that require conversion and OCR
# Convert PDF pages to images
doc = fitz.open("aapl-20240928.pdf")

# Extract text from each page
extracted_text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text("text")  # Extract text
    extracted_text += f"\n--- Page {page_num + 1} ---\n"
    extracted_text += text

# Print some information 
print(f"The first 100 characters of the extracted text:\n{extracted_text[:100]}")
print(f"\nThe total number of characters in the extracted text: {len(extracted_text)}")

# Save
with open("aapl_annual_report.txt", "w", encoding="utf-8") as txt_file:
    txt_file.write(extracted_text)
