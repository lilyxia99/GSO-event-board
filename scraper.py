import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
from config import LOCATION, SEARCH_RADIUS, HEADLESS, BROWSER_TIMEOUT, IMAGES_DIR

class FacebookEventScraper:
    def __init__(self):
        self.setup_driver()
        self.events = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(BROWSER_TIMEOUT)
        
    def scrape_events(self):
        """Scrape Facebook events for Greensboro, NC"""
        try:
            # Navigate to Facebook events search
            search_url = f"https://www.facebook.com/events/search/?q={LOCATION.replace(' ', '%20')}"
            self.driver.get(search_url)
            time.sleep(5)
            
            # Scroll to load more events
            self._scroll_and_load()
            
            # Extract event data
            self._extract_event_data()
            
        except Exception as e:
            print(f"Error scraping events: {e}")
        finally:
            self.driver.quit()
            
        return self.events
    
    def _scroll_and_load(self):
        """Scroll page to load more events"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1
    
    def _extract_event_data(self):
        """Extract event information from the page"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Find event containers (Facebook's structure changes frequently)
        event_containers = soup.find_all('div', {'role': 'article'}) or soup.find_all('div', class_=lambda x: x and 'event' in x.lower())
        
        for container in event_containers:
            event_data = self._parse_event_container(container)
            if event_data:
                self.events.append(event_data)
    
    def _parse_event_container(self, container):
        """Parse individual event container"""
        try:
            event = {
                'title': '',
                'date': '',
                'time': '',
                'location': '',
                'description': '',
                'image_url': '',
                'event_url': '',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract title
            title_elem = container.find('a', {'role': 'link'}) or container.find('h3')
            if title_elem:
                event['title'] = title_elem.get_text(strip=True)
            
            # Extract image URL
            img_elem = container.find('img')
            if img_elem and img_elem.get('src'):
                event['image_url'] = img_elem['src']
            
            # Extract event URL
            link_elem = container.find('a', href=True)
            if link_elem:
                event['event_url'] = link_elem['href']
                if not event['event_url'].startswith('http'):
                    event['event_url'] = 'https://facebook.com' + event['event_url']
            
            # Only return events with at least a title
            if event['title']:
                return event
                
        except Exception as e:
            print(f"Error parsing event container: {e}")
        
        return None
    
    def download_event_images(self):
        """Download event poster images"""
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
            
        for i, event in enumerate(self.events):
            if event.get('image_url'):
                try:
                    response = requests.get(event['image_url'], timeout=10)
                    if response.status_code == 200:
                        filename = f"event_{i}_{int(time.time())}.jpg"
                        filepath = os.path.join(IMAGES_DIR, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        event['local_image_path'] = filepath
                        print(f"Downloaded image for: {event['title']}")
                        
                except Exception as e:
                    print(f"Error downloading image for {event['title']}: {e}")

if __name__ == "__main__":
    scraper = FacebookEventScraper()
    events = scraper.scrape_events()
    scraper.download_event_images()
    print(f"Scraped {len(events)} events")
