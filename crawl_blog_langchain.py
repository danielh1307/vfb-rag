import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from langchain.schema import Document
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Base URL for the VfB website
BASE_URL = "https://www.vfb.de/de/1893/aktuell/neues/"

# Create a directory to store blog articles if it doesn't exist
OUTPUT_DIR = "blog_articles_langchain"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Maximum number of articles to process
MAX_ARTICLES = 3

def setup_driver():
    """Set up and return a configured Selenium WebDriver."""
    chrome_options = Options()
    # Uncomment the line below to run in headless mode (no GUI)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def load_page_with_selenium(url: str, wait_time: int = 5) -> Document:
    """Load a page using Selenium and return a LangChain Document."""
    driver = setup_driver()
    try:
        # Navigate to the page
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Give additional time for all content to load
        time.sleep(wait_time)
        
        # Get the page source
        page_source = driver.page_source
        
        # Create a LangChain Document
        return Document(
            page_content=page_source,
            metadata={"source": url}
        )
    finally:
        driver.quit()

def extract_article_links(html_content: str) -> List[str]:
    """Extract article links from the main page."""
    soup = BeautifulSoup(html_content, "html.parser")
    article_links = []
    
    # Find all article elements
    articles = soup.select("article.teaserArchiveArticle")
    for article in articles:
        link = article.select_one("a[href*='/aktuell/neues/']")
        if link and link.get("href"):
            full_url = urljoin(BASE_URL, link["href"])
            article_links.append(full_url)
    
    return article_links[:MAX_ARTICLES]

def extract_article_data(html_content: str, url: str) -> Dict[str, Any]:
    """Extract relevant data from an article page."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract title
    title = ""
    title_element = soup.select_one("div.teaser h1")
    if title_element:
        title = title_element.text.strip()
    
    # Extract date
    date = ""
    date_element = soup.select_one(".date")
    if date_element:
        date = date_element.text.strip()
    
    # Extract content
    content = ""
    content_div = soup.select_one("div.content")
    if content_div:
        paragraphs = content_div.select("div.meldung-bild p, p")
        for p in paragraphs:
            if p.text.strip():
                content += p.text.strip() + "\n\n"
    
    # Extract categories
    categories = []
    category_elements = soup.select(".directories a")
    for category_element in category_elements:
        categories.append(category_element.text.strip())
    
    # Extract image URL
    image_url = ""
    image_element = soup.select_one(".image img")
    if image_element and image_element.get("src"):
        image_url = urljoin(url, image_element["src"])
    
    return {
        "title": title,
        "url": url,
        "date": date,
        "content": content.strip(),
        "categories": categories,
        "image_url": image_url
    }

def save_article(article_data: Dict[str, Any]) -> None:
    """Save article data to a JSON file."""
    # Create a filename from the title
    filename = article_data["title"].lower()
    filename = "".join(c if c.isalnum() or c in ["-", "_"] else "_" for c in filename)
    filename = f"{filename}.json"
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)
    print(f"Saved article to {file_path}")

def crawl_blog_articles() -> None:
    """Crawl blog articles from the VfB Stuttgart website using Selenium."""
    try:
        # Load the main page
        main_page = load_page_with_selenium(BASE_URL, wait_time=5)
        
        # Extract article links
        article_links = extract_article_links(main_page.page_content)
        print(f"Found {len(article_links)} articles")
        
        # Process each article
        for url in article_links:
            print(f"\nProcessing article: {url}")
            try:
                # Load the article page
                article_page = load_page_with_selenium(url, wait_time=3)
                
                # Extract and save article data
                article_data = extract_article_data(article_page.page_content, url)
                save_article(article_data)
                
            except Exception as e:
                print(f"Error processing article {url}: {str(e)}")
                continue
        
    except Exception as e:
        print(f"Error crawling blog articles: {str(e)}")

if __name__ == "__main__":
    crawl_blog_articles() 