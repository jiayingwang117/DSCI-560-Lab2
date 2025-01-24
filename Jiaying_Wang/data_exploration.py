import requests
import pandas as pd
from bs4 import BeautifulSoup
import pdfplumber

## i. retriving CSV from Alpha Vantage
API_KEY = "UZASGLAPFRZXMYJ1"  
symbol = "TSLA"
url = "https://www.alphavantage.co/query"

params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": symbol,
    "outputsize": "compact",  # 'compact' returns the last 100 days; use 'full' for entire history
    "apikey": API_KEY
}

response = requests.get(url, params=params)
data = response.json()

if "Time Series (Daily)" in data:
    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df.index = pd.to_datetime(df.index)
    df.to_csv(f"{symbol}_stock_data.csv")
    print(f"Data saved to {symbol}_stock_data.csv")
    print(df.head())
    print("\nDataset dimensions (rows, columns):")
    print(df.shape)
    print("\nMissing values in each column:")
    print(df.isnull().sum())
    print("\nChecking for duplicate rows:")
    print(df.duplicated().sum())

else:
    print("Error:", data)


## ii. retriving from yahoo finance HTML 
URL = "https://finance.yahoo.com/"

# User-Agent header to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(URL, headers=HEADERS)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all news articles
    articles = soup.find_all("li", class_="story-item headlineFz-small yf-1m9jpnz")

    news_data = []

    for article in articles:
        # Extract headline and link
        headline_tag = article.find("h3", class_="clamp tw-line-clamp-none yf-18q3fnf")
        if headline_tag:
            link_tag = headline_tag.find_parent("a")  # Get the parent <a> tag of the headline
            headline = headline_tag.get_text(strip=True)
            link = f"{link_tag['href']}" if link_tag and link_tag.has_attr("href") else "No Link"
        else:
            headline = "No Title"
            link = "No Link"

        # Extract publication source and time
        publishing_tag = article.find("div", class_="publishing yf-1weyqlp")
        publishing_info = publishing_tag.get_text(strip=True) if publishing_tag else "No Info"

        # Store extracted data
        news_data.append({"Headline": headline, "Link": link, "Source & Time": publishing_info})


    df = pd.DataFrame(news_data)

    # Save to CSV
    csv_filename = "yahoo_finance_news.csv"
    df.to_csv(csv_filename, index=False)

    print(f"Data saved to {csv_filename}")

    print("\nFirst 5 rows of the dataset:")
    print(df.head())

    print("\nDataset dimensions (rows, columns):")
    print(df.shape)

    print("\nMissing values in each column:")
    print(df.isnull().sum())

else:
    print(f"Failed to fetch data. Status Code: {response.status_code}")

## iii. retriving pdf downloaded from SEC EDGAR Filings
pdf_path = "tsla-20240930.pdf"

# Extract text from the PDF
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()

# Save extracted text to a file
with open("extracted_text.txt", "w") as file:
    for page in pdf.pages:
        file.write(page.extract_text())
        file.write("\n\n")
        
print("\nPDF Text extracted and saved to extracted_text.txt")


# Read extracted text from the file
with open('extracted_text.txt', "r") as file:
    extracted_text = file.read()

# Split the text into pages using the delimiter used during saving
pages = extracted_text.split("\n\n")

print("\nFirst 500 characters of the extracted text:")
print(extracted_text[:500])
num_pages = len(pages)
total_characters = len(extracted_text)
print(f"\nTotal pages extracted: {num_pages}")
print(f"Total characters extracted: {total_characters}")


empty_pages = sum(1 for page in pages if not page.strip())
print(f"\nNumber of empty pages: {empty_pages}")

word_counts = [len(page.split()) for page in pages]
average_words_per_page = sum(word_counts) / num_pages if num_pages > 0 else 0
print(f"Average words per page: {average_words_per_page:.2f}")
