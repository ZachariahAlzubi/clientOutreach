from bs4 import BeautifulSoup

import logging

import random
import time
import requests
import threading

import re
from urllib import parse

# Define a function to scrape a website for contact information
def scrape_website(url, proxies):
    time.sleep(random.uniform(1, 3))
    try:
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Problem with request: {str(e)}")
        return None
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        email_matches = re.findall(email_pattern, text)
        phone_matches = re.findall(phone_pattern, text)
        contact_link = None
        for a_tag in soup.find_all('a', href=True):
            if "contact" in a_tag.text.lower():
                contact_link = parse.urljoin(url, a_tag['href'])
                break
        return email_matches, phone_matches, contact_link
    except Exception as e:
        logging.error(f"Problem parsing response: {str(e)}")
        return None


# Similar wrapper for scrape_website
def scrape_website_with_timeout(url, timeout=60):
    result = [None]
    def job():
        result[0] = scrape_website(url)
    thread = threading.Thread(target=job)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        logging.error(f"Timeout: scrape_website took longer than {timeout} seconds.")
        return None
    else:
        return result[0]