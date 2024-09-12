# filename: amazon_price_check.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Go directly to the search results page for 'iphone 14' on Amazon
driver.get('https://www.amazon.com/s?k=iphone+14')

# Wait for the page to load and find the price of the first result
wait = WebDriverWait(driver, 10)
price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.a-price-whole'))).text

# Print the price
print('The price of the iPhone 14 on Amazon is:', price)

# Close the driver
driver.quit()