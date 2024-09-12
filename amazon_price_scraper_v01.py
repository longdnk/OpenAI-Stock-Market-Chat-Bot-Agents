from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open the Amazon website
driver.get("https://www.amazon.com")
# driver.get("https://www.amazon.com")

# Find the search box and search for 'iPhone 14'
search_box = driver.find_element(By.ID, "twotabsearchtextbox")
search_box.send_keys("iPhone 14")
search_box.send_keys(Keys.RETURN)

# Wait for the page to load
time.sleep(3)

# Find the first result and get its price
try:
    # first_result = driver.find_element(By.XPATH, "(//div[contains(@class,'s-result-item')])[1]")
    # price = first_result.find_element(By.XPATH, ".//span[@class='a-price']")
    # print("Price of iPhone 14:", price.text)
    
    wait = WebDriverWait(driver, 10)
    price = wait.until(EC.presence_of_element_located((By.XPATH, ".//span[@class='a-price']")))
    print("Price of iPhone 14:", str(price.text).split("\n"))

except Exception as e:
    print("Error finding the price:", e)

# Close the browser
driver.quit()






