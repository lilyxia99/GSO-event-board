import os
from dotenv import load_dotenv

load_dotenv()

# Facebook scraping settings
LOCATION = "Greensboro, NC"
SEARCH_RADIUS = 25  # miles

# AI API settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Output settings
SPREADSHEET_PATH = 'greensboro_events.xlsx'
IMAGES_DIR = 'event_images'

# Web server settings
HOST = '127.0.0.1'
PORT = 5000
DEBUG = True

# Browser settings
HEADLESS = True
BROWSER_TIMEOUT = 30
