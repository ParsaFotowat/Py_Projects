import requests
from bs4 import BeautifulSoup
import pandas as pd
import random

class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.user_agent = self.user_agent_spoofing()

    def user_agent_spoofing(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36"
        ]
        return random.choice(user_agents)

    def scrape_data(self, url, tags, data_type):
        headers = {'User-Agent': self.user_agent}
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching URL: {e}")

        soup = BeautifulSoup(response.content, 'html.parser')
        if data_type == 'text':
            elements = soup.select(tags)
            if not elements:
                raise Exception(f"No elements found for tags: {tags}")
            return [element.get_text(strip=True) for element in elements]
        elif data_type == 'images':
            elements = soup.select(tags)
            if not elements:
                raise Exception(f"No images found for tags: {tags}")
            return [img['src'] for img in elements if img.has_attr('src')]
        elif data_type == 'tables':
            try:
                tables = pd.read_html(response.content)
                if not tables:
                    raise Exception("No tables found on the page.")
                return tables
            except ValueError:
                raise Exception("No tables found on the page.")
        else:
            raise Exception(f"Unsupported data type: {data_type}")

    def retry_logic(self, url, tags, data_type, retries=3):
        for attempt in range(retries):
            try:
                return self.scrape_data(url, tags, data_type)
            except Exception as e:
                if attempt < retries - 1:
                    continue
                else:
                    raise Exception(f"Failed after {retries} attempts: {e}")