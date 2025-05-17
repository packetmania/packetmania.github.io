import time
import re
import requests
import argparse
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; PacketCrawler/1.0)"
}

# ----------------------------
# Get blog post URLs from sitemap
# ----------------------------
def get_post_urls(sitemap_url):
    response = requests.get(sitemap_url, headers=headers)
    soup = BeautifulSoup(response.content, 'xml')
    urls = [
        loc.text for loc in soup.find_all('loc')
        if re.search(r'/\d{4}/\d{2}/\d{2}/', loc.text)
    ]
    return urls

# ----------------------------
# Extract view count and cleaned title using Selenium
# ----------------------------
def extract_view_count(driver, url, keyword):
    try:
        driver.get(url)
        time.sleep(2)

        raw_title = driver.title.strip()
        title = re.sub(r'\s*\|\s*.*$', '', raw_title)  # Strip trailing " | Something"

        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]/..")
        for el in elements:
            full_text = el.text
            match = re.search(rf"{re.escape(keyword)}\s*(\d+)", full_text)
            if match:
                views = int(match.group(1))
                return views, title

    except Exception as e:
        print(f"Error processing {url}: {e}")
    return None, None

# ----------------------------
# Main crawler logic
# ----------------------------
def crawl_packetmania(lang="zh"):
    base_url = "https://www.packetmania.net" if lang == "zh" else "https://www.packetmania.net/en"
    sitemap_url = f"{base_url}/sitemap.xml"
    keyword = "阅读次数：" if lang == "zh" else "Views:"

    post_urls = get_post_urls(sitemap_url)
    print(f"Found {len(post_urls)} posts.\n")

    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    results = []
    for i, url in enumerate(post_urls):
        print(f"[{i+1}/{len(post_urls)}] Crawling {url}")
        views, title = extract_view_count(driver, url, keyword)
        if views is not None:
            print(f" -> Views: {views} | Title: {title}")
            results.append((url, views, title))
        else:
            print(" -> View count not found.")
        time.sleep(1)

    driver.quit()

    # Sort by view count descending
    results.sort(key=lambda x: x[1], reverse=True)

    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") 
    md_filename = f"packetmania_views_{timestamp}_{lang}.md"

    # Output Markdown table
    with open(md_filename, "w", encoding="utf-8") as f:
        if lang == "zh":
            f.write("| 排名 | 阅读次数 | 标题 |\n")
            f.write("|-----:|----------:|------|\n")
        else:
            f.write("| # | Views | Title |\n")
            f.write("|--:|------:|-------|\n")

        for idx, (url, views, title) in enumerate(results, 1):
            safe_title = title.replace("|", "-")
            f.write(f"| {idx} | {views} | [{safe_title}]({url}) |\n")

    print(f"\n✅ Markdown table written to `{md_filename}`")
    return results

# ----------------------------
# Entry Point with CLI args
# ----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PacketMania View Count Crawler")
    parser.add_argument("--lang", choices=["en", "zh"], default="zh", help="Language for scraping and output")
    args = parser.parse_args()

    crawl_packetmania(lang=args.lang)

