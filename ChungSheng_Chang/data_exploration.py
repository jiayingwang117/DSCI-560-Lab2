import os
import requests
import praw
import dotenv
import json
import csv
import pdfplumber
import yfinance as yf
from requests.auth import HTTPBasicAuth

dotenv.load_dotenv()


STOCK_SYMBOL = 'NVDA'
START_DATE = '2020-01-01'
END_DATE = '2024-12-31'
URL = 'https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2025'
DATA_PATH = 'data/'
REDDIT_COMMUNITY = 'NVDA_Stock'
PDF_PATH = 'data/NVIDIA-Investor-Presentation-Oct-2024.pdf'


def main():
    # Create data directory
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    # Get stock price data
    get_stock_price(STOCK_SYMBOL, START_DATE, END_DATE)
    # Scrape stock data
    scrape_stock_data(URL, DATA_PATH + 'nvidia_news.html')
    # Get PDF data
    get_pdf_data(PDF_PATH)
    # Get Reddit data
    get_reddit_data(REDDIT_COMMUNITY)


def get_stock_price(stock_name, start_date, end_date):
    # Get stock data from Yahoo Finance
    stock_data = yf.download(stock_name, start=start_date, end=end_date)
    stock_data.to_csv(DATA_PATH + stock_name + '_price.csv')
    print(stock_data.head())
    print(f"{STOCK_SYMBOL} data saved to {DATA_PATH + stock_name + '_price.csv'}")


def scrape_stock_data(url, file_path):
    # Scrape stock data
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'w') as file:
            file.write(response.text)
            print(f"Data saved to {file_path}")
    else:
        print("Failed to get data")
    
    with open(file_path, 'r') as file:
        content = file.read()
        print(content[:200])


def get_reddit_data(reddit_community):
    # Get credentials from environment variables
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")
    
    url = "https://www.reddit.com/api/v1/access_token"
    auth = HTTPBasicAuth(client_id, client_secret)
    headers = {"User-Agent": user_agent}
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, auth=auth, data=data, headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.json())

    # Initialize the Reddit API client
    reddit = praw.Reddit(
        client_id=client_id,  
        client_secret=client_secret,  
        user_agent=user_agent,
    )

    subreddit = reddit.subreddit(reddit_community)
    hot_posts = subreddit.hot(limit=5)
    post_data = []
    for post in hot_posts:
        post_data.append({
            "title": post.title,
            "url": post.url,
            "score": post.score,
            "comments": post.num_comments,
            "created": post.created_utc,
            "num_comments": post.num_comments,
        })

    with open(DATA_PATH + f'{STOCK_SYMBOL}_reddit_data.json', 'w') as file:
        json.dump(post_data, file, indent=4)
        print(f"Reddit data saved to {DATA_PATH + f'{STOCK_SYMBOL}_reddit_data.json'}")
    
    with open(DATA_PATH + f'{STOCK_SYMBOL}_reddit_data.csv', 'w', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["title", "url", "score", "comments", "created", "num_comments"])
        for post in post_data:
            writer.writerow([post["title"], post["url"], post["score"], post["comments"], post["created"], post["num_comments"]])
        print(f"Reddit data saved to {DATA_PATH + f'{STOCK_SYMBOL}_reddit_data.csv'}")


def get_pdf_data(pdf_path):
    # Get PDF data
    with pdfplumber.open(pdf_path) as pdf:
        extracted_data = []
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            extracted_data.append([page_num, page_text.strip()])
        print(extracted_data[:3])

    with open(DATA_PATH + 'nvidia_pdf_data.csv', 'w', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["page_num", "text"])
        writer.writerows(extracted_data)
        print(f"PDF data saved to {DATA_PATH + 'nvidia_pdf_data.csv'}")


if __name__ == '__main__':
    main()