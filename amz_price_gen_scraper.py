from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# # Setup webdriver
# # driver = webdriver.Chrome(ChromeDriverManager().install())
# driver = webdriver.Chrome()
# Set up the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# Go to Amazon
driver.get("https://www.amazon.com")

# Find the search box, enter "iPhone 13", and search
search_box = driver.find_element_by_id("twotabsearchtextbox")
search_box.send_keys("iPhone 13")
search_box.send_keys(Keys.RETURN)

# Wait for the search results to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".s-result-item")))

# Find the first result and get its price
first_result = driver.find_element_by_css_selector(".s-result-item")
price = first_result.find_element_by_css_selector(".a-price-whole").text

# Print the price
print("The price of the first listed iPhone 13 on Amazon is: $", price)

# Close the browser
driver.quit()

