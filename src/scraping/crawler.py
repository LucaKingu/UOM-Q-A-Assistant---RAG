import os
import json
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse

allowed_domain = "um.edu.mt"
visited = set()


async def scrape_page(page, url):
    print(f"Scraping: {url}")
    await page.goto(url, timeout=15000)  # 15 sec for the page to load
    # content = await page.content()

    # Extract useful data for JSON
    title = await page.title()
    headings = await page.query_selector_all("h1, h2, h3")
    links = await extract_links(page, url)
    meta_description = await page.query_selector('meta[property="og:description"]')
    description_content = (
        await meta_description.get_attribute("content")
        if meta_description else None
    )

# Try to extract content from various common selectors
    content_selectors = [
        ".sq_news_body",          # Original class
        ".content",               # General content container
        ".article-body",          # Common class for articles
        ".news-body",             # News specific
        "div.article",            # If articles use div tags with classes
        "main",                   # The <main> element often holds primary content
        "article"                 # Standard tag for articles
    ]

    # Fallback to get article content from any of the selectors above
    article_content = None
    for selector in content_selectors:
        element = await page.query_selector(selector)
        if element:
            article_content = await element.inner_text()
            break

    # If no content found, fallback to extracting text from all <p> tags
    if not article_content:
        paragraphs = await page.query_selector_all("p")
        article_content = "\n".join([await p.inner_text() for p in paragraphs])

    # Optional: Remove unwanted whitespace or clean up the content
    article_content = article_content.strip() if article_content else "No content found"

    data = {
        "url": url,
        "title": title,
        "headings": [await h.inner_text() for h in headings],
        "links": links,
        "description": description_content,  # Meta description only if found
        # Extracted content (fallbacks included)
        "content": article_content
    }

    # home will be the uom_url
    safe_name = urlparse(url).path.replace("/", "_").strip("_") or "home"
    # Should already exist with structure
    os.makedirs("Data/Raw", exist_ok=True)
    with open(f"Data/Raw/{safe_name}.json", "w", encoding="utf-8") as f:
        # This should overwrite all json files should the programme need to be re-run (No duplicates will be created)
        json.dump(data, f, ensure_ascii=False, indent=4)
    return links


async def extract_links(page, url):
    anchors = await page.query_selector_all("a")  # <a href "link">
    links = []
    for a in anchors:
        href = await a.get_attribute("href")

        # mailto is a protocol,not a domain -  which is why it gets error scraping
        if href and href.startswith("mailto:"):
            continue
        if href and (href.endswith(".pdf") or href.endswith(".docx") or href.endswith(".xlsx")):
            continue

        full_url = urljoin(url, href)
        if allowed_domain in full_url and full_url not in visited:
            links.append(full_url)
    return links


async def crawl(start_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        queue = [start_url]

        while queue:
            current_url = queue.pop(0)

            if current_url in visited:
                continue
            visited.add(current_url)

            try:
                new_links = await scrape_page(page, current_url)
                queue.extend(new_links)
            except Exception as e:
                if "Execution context was destroyed" in str(e):
                    print(
                        f"Error scraping {current_url}: {e} - Page may not exist (error 404), Check this!"
                    )
                elif "net::ERR_ABORTED" in str(e):
                    print(
                        f"Error scraping {current_url}: {e} - Check if link is a file instead of web page(such as PDF) OR if server is able to get the required page"
                    )
                else:
                    print(f"Error Scraping {current_url}: {e}")

        await browser.close()
