from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_malta_hotels(url):
    driver = setup_driver()
    hotels_data = set()
    
    try:
        driver.get(url)
        time.sleep(3)
        
        # Accept cookies
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            print("Accepted cookies")
            time.sleep(2)
        except Exception as e:
            print(f"Could not find cookie button: {e}")
        
        # Get the total height of the page
        total_height = driver.execute_script("return document.body.scrollHeight")
        scroll_pause_time = 2
        
        for scroll in range(3):
            print("\n" + "="*50)
            print(f"DEBUG: Starting scroll {scroll + 1}")
            
            # Calculate scroll position to stay above bottom
            current_position = driver.execute_script("return window.pageYOffset;")
            scroll_amount = min(1000, (total_height * 0.7) - current_position)  # Stay within 70% of page height
            
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(scroll_pause_time)
            
            # Get hotels
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            property_cards = soup.select('div[data-testid="property-card"]')
            print(f"DEBUG: Found {len(property_cards)} hotels after scroll")
            
            # Process hotels
            hotels_before = len(hotels_data)
            for card in property_cards:
                try:
                    hotel_data = (
                        card.select_one('div[data-testid="title"]').text.strip(),
                        card.select_one('span[data-testid="price-and-discounted-price"]').text.strip(),
                        card.select_one('div[data-testid="review-score"]').text.strip() if card.select_one('div[data-testid="review-score"]') else 'No rating',
                        card.select_one('span[data-testid="address"]').text.strip() if card.select_one('span[data-testid="address"]') else 'No address'
                    )
                    hotels_data.add(hotel_data)
                except Exception as e:
                    continue
            
            hotels_added = len(hotels_data) - hotels_before
            print(f"New unique hotels added: {hotels_added}")
            print(f"Total unique hotels so far: {len(hotels_data)}")
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'malta_hotels_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Price', 'Rating', 'Address'])
                writer.writerows(hotels_data)
            
            print(f"\nData saved to {filename}")
            print(f"Total unique hotels found: {len(hotels_data)}")
        
    finally:
        driver.quit()

# Run the scraper
url = "https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAQoggJCDHNlYXJjaF9tYWx0YUgzWARonAGIAQGYAQm4AQfIAQzYAQHoAQH4AQOIAgGoAgO4Apj9gLoGwAIB0gIkOWQ0NTFmM2ItNGExZC00N2MwLWJiZjItOTRhM2I0NmE3MTc52AIF4AIB&ss=Malta&checkin=2025-03-01&checkout=2025-03-02&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D204%3Bprice%3DEUR-140-max-1"
scrape_malta_hotels(url)