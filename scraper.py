import time
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from database import connect_to_db
from sentiment_analysis import analyze_sentiment

# Setup Selenium WebDriver with User-Agent rotation
def get_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument(f"user-agent={UserAgent().random}")  # Rotate User-Agent

    # Use Service() class to specify ChromeDriver location
    service = Service(ChromeDriverManager().install())

    # Now pass `options` and `service` arguments correctly
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Function to parse reviews from an Amazon page
def parse_reviews(driver, page_number):
    url = f"https://www.amazon.in/Apple-New-iPhone-12-128GB/dp/B08L5TNJHG?pageNumber={page_number}"
    driver.get(url)
    
    # Explicit wait: wait for the review elements to be present
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.review-text-content'))
        )

        reviews = []

        review_elements = driver.find_elements(By.CSS_SELECTOR, '.review-text-content')

        for review in review_elements:
            try:
                # Attempt to extract the review title using XPath for better accuracy
                title_element = review.find_element(By.XPATH, ".//ancestor::div[contains(@class, 'review')]//a[contains(@class, 'a-text-bold')]")
                title = title_element.text if title_element else 'No Title Found'  # Use title if exists
            except Exception as e:
                title = 'No Title Found'  # Default title if error occurs

            # Corrected CSS selector for the review text
            review_text_element = WebDriverWait(review, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.a-expander-content.review-text-content span'))
            )
            review_text = review_text_element.text
            style_name = "128GB"  # Static for this model, can be dynamic if needed
            colour = "Black"  # Static for this model, can be dynamic if needed
            verified_purchase = 'Yes' if "Verified Purchase" in review.text else 'No'
            
            # Analyze sentiment of the review text
            sentiment = analyze_sentiment(review_text)

            reviews.append((title, review_text, style_name, colour, verified_purchase, sentiment))

    except Exception as e:
        print(f"Error parsing reviews on page {page_number}: {e}")
        reviews = []

    return reviews

# Function to save reviews to the database
def save_reviews_to_db(reviews):
    connection = connect_to_db()
    if connection is None:
        print("Error: Unable to connect to the database.")
        return

    cursor = connection.cursor()
    insert_query = """
        INSERT INTO reviews (title, review_text, style_name, colour, verified_purchase, sentiment)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(insert_query, reviews)
        connection.commit()
        print(f"Inserted {len(reviews)} reviews into the database.")
    except mysql.connector.Error as e:
        print(f"Error inserting reviews into the database: {e}")
    finally:
        cursor.close()
        connection.close()

# Function to check if there is a next page
def has_next_page(driver):
    try:
        next_button = driver.find_element(By.CLASS_NAME, 'a-last')
        next_button_class = next_button.get_attribute('class')
        print(f"Next Button Class: {next_button_class}")  # Debug print to check if next page button exists
        return 'a-disabled' not in next_button_class  # Check if 'Next' is disabled
    except Exception as e:
        print(f"Error finding next page: {e}")
        return False  # No "Next" button, hence no more pages

# Main scraping function
def scrape_all_reviews():
    page_number = 1
    driver = get_driver()

    while True:
        print(f"Scraping reviews from page {page_number}...")
        reviews = parse_reviews(driver, page_number)

        if not reviews:
            print(f"No more reviews found on page {page_number}. Stopping.")
            break

        # Save reviews to the database
        save_reviews_to_db(reviews)
        
        page_number += 1

        # Check for next page and proceed
        if not has_next_page(driver):
            print(f"End of reviews. Stopping after page {page_number}.")
            break

        time.sleep(2)  # Add delay to avoid too many requests in a short period

    driver.quit()  # Close the WebDriver

if __name__ == "__main__":
    scrape_all_reviews()
