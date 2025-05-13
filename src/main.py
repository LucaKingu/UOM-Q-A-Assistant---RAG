import os
import asyncio
from dotenv import load_dotenv
from scraping.crawler import crawl


load_dotenv()

weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
weaviate_URL = os.getenv("WEAVIATE_URL")

huggingface_api_key = os.getenv("HUGGINGFACE_API_TOKEN")

app_port = os.getenv("PORT")  # May not need this
uom_url = "https://www.um.edu.mt/"


def main():
    asyncio.run(crawl(uom_url))


if __name__ == '__main__':
    main()
