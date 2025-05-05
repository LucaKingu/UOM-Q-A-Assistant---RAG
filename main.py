import os
from dotenv import load_dotenv

load_dotenv()

weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
weaviate_URL = os.getenv("WEAVIATE_URL")

huggingface_api_key = os.getenv("HUGGINGFACE_API_TOKEN")

app_port = os.getenv("PORT")


def main():
    print("Weaviate API Key:", weaviate_api_key)
    print("Weaviate URL:", weaviate_URL)
    print("HuggingFace API Token:", huggingface_api_key)
    print("App Port:", app_port)


if __name__ == '__main__':
    main()
