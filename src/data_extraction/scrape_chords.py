from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

url = 'https://chordu.com/chords-tabs-celeste-piano-collections-11-reach-for-the-summit-lena-raine-trevor-alan-gomes--id_tZEW4X7RGMs?vers=sim'  # Replace with the URL of the webpage you want to scrape

# Set up the Selenium WebDriver
driver = webdriver.Chrome()  # Make sure to have ChromeDriver installed and in your PATH
driver.get(url)

# Scroll down the page to trigger dynamic content loading
for _ in range(1):  # You may need to adjust the number of scrolls based on the page structure
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(1)  # Add a short delay to allow content to load

# Get the updated page source with dynamically loaded content
page_source = driver.page_source

# Close the browser window
driver.quit()

# Now, parse the updated page source using BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Find all spans with dynamic IDs matching the pattern 'ac{idx}'
spans = soup.find_all('span', {'id': lambda x: x and x.startswith('ac')})

data_list = []

for span in spans:
    # Find the <p> tag inside the <span>
    p_tag = span.find('p')

    # Extract and append the content to the list
    if p_tag:
        data_list.append(p_tag.get_text(strip=True) or "_")

print(data_list)