import os
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse

allowed_domain = "um.edu.mt"
visited = set()


async def scrape_page(page, url):
    print(f"Scraping: {url}")
    await page.goto(url, timeout=15000)  # 15 sec for the page to load
    content = await page.content()

    # home will be the uom_url
    safe_name = urlparse(url).path._replace("/", "_").strip("_") or "home"
    # Should already exist with structure
    os.makedirs("Data/Raw", exist_ok=True)
    with open(f"Data/Raw/{safe_name}.json", "w", encoding="utf-8") as f:
        f.write(content)

    anchors = await page.query_selector_all("a")  # <a href "link">
    links = []
    for a in anchors:
        href = await a.get_attribute("href")
        if href:
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
                print(f"Error Scraping {current_url}: {e}")

        await browser.close()
