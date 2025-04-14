import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Base URL for the VfB website
BASE_URL = "https://www.vfb.de/de/1893/aktuell/neues/"

# Create a directory to store blog articles if it doesn't exist
OUTPUT_DIR = "blog_articles"
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

def save_page_source(driver, filename):
    """Save the current page source to a file for debugging."""
    debug_dir = os.path.join(OUTPUT_DIR, "debug")
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    
    file_path = os.path.join(debug_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"Saved page source to {file_path}")

def safe_find_element(element, by, value, max_retries=3):
    """Safely find an element with retry logic for stale elements."""
    for attempt in range(max_retries):
        try:
            return element.find_element(by, value)
        except StaleElementReferenceException:
            if attempt < max_retries - 1:
                print(f"Stale element reference, retrying... (attempt {attempt+1}/{max_retries})")
                time.sleep(1)
            else:
                print(f"Failed to find element after {max_retries} attempts")
                return None
    return None

def safe_find_elements(element, by, value, max_retries=3):
    """Safely find elements with retry logic for stale elements."""
    for attempt in range(max_retries):
        try:
            return element.find_elements(by, value)
        except StaleElementReferenceException:
            if attempt < max_retries - 1:
                print(f"Stale element reference, retrying... (attempt {attempt+1}/{max_retries})")
                time.sleep(1)
            else:
                print(f"Failed to find elements after {max_retries} attempts")
                return []
    return []

def extract_article_data(article_element, driver):
    """Extract relevant data from an article element based on the known structure."""
    try:
        # Extract title
        title_element = safe_find_element(article_element, By.CSS_SELECTOR, ".title")
        if not title_element:
            print("Could not find title element")
            return None
        title = title_element.text.strip()
        
        # Extract URL from the main link
        link_element = safe_find_element(article_element, By.CSS_SELECTOR, "a[href*='/aktuell/neues/']")
        if not link_element:
            print("Could not find link element")
            return None
        article_url = link_element.get_attribute("href")
        
        # Extract date
        date = ""
        date_element = safe_find_element(article_element, By.CSS_SELECTOR, ".date")
        if date_element:
            date = date_element.text.strip()
        
        # Extract summary
        summary = ""
        summary_element = safe_find_element(article_element, By.CSS_SELECTOR, ".text p")
        if summary_element:
            summary = summary_element.text.strip()
        
        # Extract image URL if available
        image_url = ""
        image_element = safe_find_element(article_element, By.CSS_SELECTOR, ".image img")
        if image_element:
            image_url = image_element.get_attribute("src")
        
        # Extract categories
        categories = []
        category_elements = safe_find_elements(article_element, By.CSS_SELECTOR, ".directories a")
        for category_element in category_elements:
            categories.append(category_element.text.strip())
        
        return {
            "title": title,
            "url": article_url,
            "date": date,
            "summary": summary,
            "image_url": image_url,
            "categories": categories
        }
    except Exception as e:
        print(f"Error extracting article data: {str(e)}")
        return None

def extract_article_content(driver, article_url):
    """Extract the full content of an article from its page."""
    try:
        # Navigate to the article page
        print(f"Navigating to article: {article_url}")
        driver.get(article_url)
        
        # Wait for the content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Give additional time for all content to load
        time.sleep(3)
        
        # Get the article content
        article_html = driver.page_source
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(article_html, "html.parser")
        
        # Find the main content div
        content_div = soup.select_one("div.content")
        if not content_div:
            print("Could not find content div")
            return {
                "title": "",
                "content": ""
            }
        
        # Extract the article title
        title = ""
        title_element = content_div.select_one("div.teaser h1")
        if title_element:
            title = title_element.text.strip()
        
        # Extract the article text
        article_text = ""
        
        # Find all paragraphs in the content
        paragraphs = content_div.select("div.meldung-bild p")
        if paragraphs:
            for p in paragraphs:
                # Skip empty paragraphs
                if p.text.strip():
                    article_text += p.text.strip() + "\n\n"
        
        # If no paragraphs found in meldung-bild, try other selectors
        if not article_text:
            paragraphs = content_div.select("p")
            for p in paragraphs:
                # Skip empty paragraphs
                if p.text.strip():
                    article_text += p.text.strip() + "\n\n"
        
        # Clean up the text
        article_text = article_text.strip()
        
        return {
            "title": title,
            "content": article_text
        }
    except Exception as e:
        print(f"Error extracting article content: {str(e)}")
        return {
            "title": "",
            "content": ""
        }

def crawl_blog_articles():
    """Crawl blog articles from the VfB Stuttgart website."""
    driver = setup_driver()
    
    try:
        # Navigate to the blog page
        print(f"Navigating to {BASE_URL}...")
        driver.get(BASE_URL)
        
        # Wait for the page to load
        print("Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Give additional time for all content to load
        time.sleep(5)
        
        # Save the page source for debugging
        save_page_source(driver, "initial_page.html")
        
        # First, find the wrapper meldung div
        wrapper_elements = driver.find_elements(By.CSS_SELECTOR, "div.wrapper.meldung")
        if not wrapper_elements:
            print("Could not find wrapper.meldung div")
            return
        
        print(f"Found {len(wrapper_elements)} wrapper.meldung divs")
        
        # Then, find the articles div inside the wrapper
        articles_div = None
        for wrapper in wrapper_elements:
            try:
                articles_div = wrapper.find_element(By.CSS_SELECTOR, "div.articles")
                if articles_div:
                    print("Found articles div inside wrapper.meldung")
                    break
            except:
                continue
        
        if not articles_div:
            print("Could not find articles div inside wrapper.meldung")
            return
        
        # Find all article elements
        article_elements = articles_div.find_elements(By.CSS_SELECTOR, "article.teaserArchiveArticle")
        total_articles = len(article_elements)
        print(f"Found {total_articles} articles in total")
        
        # Limit to the first MAX_ARTICLES
        article_elements = article_elements[:MAX_ARTICLES]
        print(f"Processing only the first {len(article_elements)} articles")
        
        # Extract data from each article
        articles = []
        
        # First, collect all article URLs to avoid stale element issues
        article_urls = []
        for article_element in article_elements:
            try:
                link_element = safe_find_element(article_element, By.CSS_SELECTOR, "a[href*='/aktuell/neues/']")
                if link_element:
                    article_url = link_element.get_attribute("href")
                    article_urls.append(article_url)
                    print(f"Found article URL: {article_url}")
            except Exception as e:
                print(f"Error getting article URL: {str(e)}")
        
        print(f"Collected {len(article_urls)} article URLs")
        
        # Now process each article URL
        for i, article_url in enumerate(article_urls):
            print(f"Processing article {i+1}/{len(article_urls)}")
            
            # Navigate to the article page
            print(f"Navigating to article: {article_url}")
            driver.get(article_url)
            
            # Wait for the content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give additional time for all content to load
            time.sleep(3)
            
            # Extract the article content
            content_data = extract_article_content(driver, article_url)
            
            # Navigate back to the main page
            print("Navigating back to main page...")
            driver.get(BASE_URL)
            
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give additional time for all content to load
            time.sleep(3)
            
            # Find the article element again
            wrapper_elements = driver.find_elements(By.CSS_SELECTOR, "div.wrapper.meldung")
            articles_div = None
            for wrapper in wrapper_elements:
                try:
                    articles_div = wrapper.find_element(By.CSS_SELECTOR, "div.articles")
                    if articles_div:
                        break
                except:
                    continue
            
            if not articles_div:
                print("Could not find articles div inside wrapper.meldung")
                continue
            
            article_elements = articles_div.find_elements(By.CSS_SELECTOR, "article.teaserArchiveArticle")
            if i >= len(article_elements):
                print(f"Article index {i} out of range")
                continue
            
            article_element = article_elements[i]
            article_data = extract_article_data(article_element, driver)
            
            if article_data:
                # Add the content to the article data
                article_data["full_title"] = content_data["title"]
                article_data["content"] = content_data["content"]
                
                articles.append(article_data)
                print(f"Extracted article: {article_data['title']}")
        
        # Save the articles to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(OUTPUT_DIR, f"vfb_articles_{timestamp}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(articles)} articles to {output_file}")
        
        # Also save individual HTML files for each article
        for article in articles:
            try:
                # Navigate to the article page
                print(f"Navigating to article: {article['url']}")
                driver.get(article["url"])
                
                # Wait for the content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Give additional time for all content to load
                time.sleep(3)
                
                # Get the article content
                article_html = driver.page_source
                
                # Create a filename from the title
                filename = article["title"].lower().replace(" ", "_")
                filename = "".join(c for c in filename if c.isalnum() or c == "_")
                filename = f"{filename}.html"
                
                # Save the article HTML
                article_file = os.path.join(OUTPUT_DIR, filename)
                with open(article_file, "w", encoding="utf-8") as f:
                    f.write(article_html)
                
                # Also save the extracted content as a text file
                content_file = os.path.join(OUTPUT_DIR, f"{filename.replace('.html', '.txt')}")
                with open(content_file, "w", encoding="utf-8") as f:
                    f.write(f"Title: {article['full_title']}\n\n")
                    f.write(article["content"])
                
                print(f"Saved article: {article['title']}")
            except Exception as e:
                print(f"Error saving article {article['title']}: {str(e)}")
    
    except Exception as e:
        print(f"Error during crawling: {str(e)}")
    
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    crawl_blog_articles() 