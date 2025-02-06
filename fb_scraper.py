from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json
from datetime import datetime

class FacebookAdScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None
        self.ads_data = []
        
    def setup_driver(self):
        options = Options()
        options.add_argument('--disable-notifications')
        options.add_argument('--start-maximized')
        # options.add_argument('--headless')  # Uncomment to run in headless mode
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def wait_and_find_element(self, by, value, timeout=10):
        """Helper method to wait for and find an element"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {value}")
            return None

    def login(self):
        try:
            print("Attempting to log in...")
            self.driver.get('https://www.facebook.com')
            
            # Enter email
            email_field = self.wait_and_find_element(By.ID, 'email')
            if not email_field:
                return False
            email_field.send_keys(self.email)
            
            # Enter password
            password_field = self.wait_and_find_element(By.ID, 'pass')
            if not password_field:
                return False
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.wait_and_find_element(By.NAME, 'login')
            if not login_button:
                return False
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            print("Login successful!")
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def navigate_to_ad_library(self):
        try:
            print("Navigating to Ad Library...")
            self.driver.get('https://www.facebook.com/ads/library/')
            time.sleep(5)  # Wait for page to load
            
            # Search for a broad term to get ads
            search_box = self.wait_and_find_element(By.CSS_SELECTOR, 'input[type="search"]')
            if search_box:
                search_box.send_keys("all ads")
                search_box.send_keys(Keys.RETURN)
                time.sleep(5)  # Wait for search results
                print("Successfully navigated to Ad Library and performed search")
                return True
            return False
        except Exception as e:
            print(f"Navigation failed: {str(e)}")
            return False
    
    def scrape_ads(self, num_ads=100):
        print(f"Starting to scrape {num_ads} ads...")
        try:
            ads_scraped = 0
            retry_count = 0
            max_retries = 5
            
            while ads_scraped < num_ads and retry_count < max_retries:
                # Wait for ad containers to load
                try:
                    # Try different selectors that might contain ads
                    selectors = [
                        '[role="article"]',
                        '[data-testid="ad_library_preview"]',
                        '.x1yztbdb'  # Facebook's class for ad containers
                    ]
                    
                    ad_containers = []
                    for selector in selectors:
                        try:
                            containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if containers:
                                ad_containers = containers
                                break
                        except:
                            continue
                    
                    if not ad_containers:
                        print("No ads found, retrying...")
                        retry_count += 1
                        time.sleep(3)
                        continue
                    
                    print(f"Found {len(ad_containers)} ad containers")
                    
                    for ad in ad_containers:
                        try:
                            # Extract ad information with multiple fallback selectors
                            ad_data = {
                                'timestamp': datetime.now().isoformat(),
                                'platform': 'Facebook',
                            }
                            
                            # Try to get advertiser name
                            try:
                                ad_data['advertiser'] = ad.find_element(By.CSS_SELECTOR, 
                                    'a[role="link"], .x1heor9g, .x1iorvi4').text
                            except:
                                ad_data['advertiser'] = "Unknown"
                            
                            # Try to get ad text
                            try:
                                ad_data['text_content'] = ad.find_element(By.CSS_SELECTOR, 
                                    '[data-ad-preview="message"], .x5yr21d, .xdj266r').text
                            except:
                                ad_data['text_content'] = ""
                            
                            # Only add if we got some content
                            if ad_data['text_content'] or ad_data['advertiser'] != "Unknown":
                                self.ads_data.append(ad_data)
                                ads_scraped += 1
                                print(f"Successfully scraped ad {ads_scraped}/{num_ads}")
                            
                            if ads_scraped >= num_ads:
                                break
                                
                        except Exception as e:
                            print(f"Error scraping individual ad: {str(e)}")
                            continue
                    
                    # Scroll to load more ads
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"Error finding ad containers: {str(e)}")
                    retry_count += 1
                    time.sleep(3)
                
        except Exception as e:
            print(f"Error in scraping process: {str(e)}")
        
        finally:
            print(f"Scraping completed. Total ads scraped: {len(self.ads_data)}")
            return self.ads_data
    
    def save_to_csv(self, filename='facebook.csv'):
        """Save scraped data to CSV file"""
        df = pd.DataFrame(self.ads_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
     
    def cleanup(self):
        """Close the browser and clean up"""
        if self.driver:
            self.driver.quit()

def main():
    # Replace these with your Facebook credentials
    EMAIL = "priyakannanq@gmail.com.com"    # Replace with your Facebook email
    PASSWORD = "tom&jerry_since9nov2022"      # Replace with your Facebook password
    
    # Initialize scraper with your credentials
    scraper = FacebookAdScraper(
        email=EMAIL,
        password=PASSWORD
    )
    
    try:
        # Setup and login
        scraper.setup_driver()
        if not scraper.login():
            raise Exception("Login failed")
            
        # Navigate to Ad Library
        if not scraper.navigate_to_ad_library():
            raise Exception("Navigation to Ad Library failed")
            
        # Scrape ads (you can adjust the number of ads to scrape)
        ads = scraper.scrape_ads(num_ads=100)
        
        # Save data
        if ads:
            scraper.save_to_csv()
            scraper.save_to_json()
        else:
            print("No ads were scraped!")
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")
        
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()