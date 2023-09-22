from bs4 import BeautifulSoup
import logging
import random
import requests
import time

import re
import threading
from urllib import parse


# Define a function to search Google
def google_search(company_name,  proxies):
    time.sleep(random.uniform(1, 3))
    url = 'https://www.google.com/search'
    try:
        response = requests.get(url, params={'q': company_name}, proxies=proxies)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Problem with request: {str(e)}")
        return None
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('div', class_='kCrYT')
        first_link = None
        for link in links:
            a_tag = link.find('a')
            if a_tag is None:  
                continue
            url = a_tag.get('href')  
            url = re.sub(r"/url\?q=([^&]*)&sa=.*", r"\1", url)
            if any(substring in url.lower() for substring in ["orginization", "company","thebluebook","profile","directory","directories","zoom","info","indeed","vendor","companies","yelp","youtube", "google", "wikipedia", "facebook", "instagram", "linkedin", "twitter"]):
                continue

            # Split the company name into words of length greater than 5
            words = [word for word in company_name.split() if len(word) > 5]

            # Get the URL's domain
            domain = parse.urlparse(url).netloc

            # If any word from the company name appears in the domain, choose this URL
            if any(word.lower() in domain.lower() for word in words):
                return url
            if first_link is None:
                first_link = url
        return first_link if first_link is not None else "No relevant link found"
    except Exception as e:
        logging.error(f"Problem parsing response: {str(e)}")
        return None


# Define a wrapper function to call google_search with a timeout
def google_search_with_timeout(row, timeout=60):
    result = [None]
    def job():
        result[0] = google_search(row['Legal Business Name'])
    thread = threading.Thread(target=job)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        logging.error(f"Timeout: google_search took longer than {timeout} seconds.")
        return None
    else:
        return result[0]