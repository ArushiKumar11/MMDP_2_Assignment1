import os
import requests
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import re

nltk.download('stopwords')
#"sports":['https://www.livescore.com']
# "finance":['https://www.financialexpress.com']
#  "education":['https://www.edutopia.org/']
#  "science":['https://science.nasa.gov/']
# "travel" = ['https://www.easemytrip.com/']
# "politics":['https://www.npr.org/sections/politics/']
# "business":['https://www.startupindia.gov.in/', 'https://www.msn.com/en-us/money]
# "art":["https://www.nga.gov/"]
#"movies":["https://www.themoviedb.org/"]
# "gaming":["https://primegaming.blog/","https://gamerant.com/","https://www.pcgamer.com/""https://www.n4g.com/"]
#"cars":["https://cars.tatamotors.com/"]
#"food":["https://pinchofyum.com/"]
#"history":["https://www.worldhistory.org/"]


categories = {
   "history":["https://www.historyextra.com/"]
}

# Paths
base_path = os.path.join(os.getcwd(), "B_TextDataset")
data_path = os.path.join(base_path, "data")

# Preprocessing function
def clean_text(text):
    text = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove punctuation
    text = text.lower()  # Lowercase
    text = ' '.join(word for word in text.split() if word not in stopwords.words('english'))  # Remove stopwords
    return text

# Scraping function
def scrape_text(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else "No Title"
            
            # Extract article content (from paragraphs)
            paragraphs = soup.find_all('p')
            content = ' '.join(p.get_text() for p in paragraphs)
            
            # Try different content selectors if paragraphs are empty
            if not content.strip():
                # Try article tags
                article = soup.find('article')
                if article:
                    content = article.get_text()
                else:
                    # Try div with common content class names
                    content_div = soup.find('div', class_=re.compile('(content|article|main|story|post)'))
                    if content_div:
                        content = content_div.get_text()
                    else:
                        content = "No content found"

            # Clean content
            clean_content = clean_text(content)

            return title, clean_content
        else:
            print(f"Failed to access {url}: Status code {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

# Crawl and save data
total_articles = 0
successful_categories = 0

for category, urls in categories.items():
    category_articles = 0
    text_file_path = os.path.join(data_path, f"{category}.txt")
    
    print(f"\nProcessing category: {category}")
    
    try:
        with open(text_file_path, "w", encoding="utf-8") as file:
            for url in urls:
                print(f"  Scraping: {url}")
                title, content = scrape_text(url)
                if content and len(content) > 100:  # Ensure we have substantial content
                    file.write(f"Title: {title}\n\n")
                    file.write(f"{content}\n\n")
                    file.write("=" * 80 + "\n\n")
                    category_articles += 1
                    total_articles += 1
                    print(f"  ✓ Success: {title[:50]}...")
                else:
                    print(f"  ✗ Failed: No substantial content found")
                
                # Use a random delay between 2-5 seconds to avoid being blocked
                delay = random.uniform(2, 5)
                print(f"  Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        if category_articles > 0:
            successful_categories += 1
            print(f"✓ Completed {category}: {category_articles} articles scraped")
        else:
            print(f"✗ No articles found for {category}")
            
    except Exception as e:
        print(f"Error processing category {category}: {e}")

print("\n" + "=" * 50)
print(f"Text dataset collection complete.")
print(f"Total articles: {total_articles}")
print(f"Categories with content: {successful_categories}/20")
print("=" * 50)