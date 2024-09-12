# filename: iphone_price.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Go to thegioididong.com
driver.get("https://www.thegioididong.com/")

# Wait until the search box is visible
wait = WebDriverWait(driver, 10)
search_box = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='text']")))

# Search for "iphone 13"
search_box.send_keys("iphone 13")
search_box.send_keys(Keys.RETURN)

# Wait for the search results to load
time.sleep(5)

# Try to find the price of the first search result
try:
    price = driver.find_element(By.CSS_SELECTOR, ".price").text
    # Print the price
    print(price)
except Exception as e:
    print("Product not found or price not available.")

# Close the driver
driver.quit()