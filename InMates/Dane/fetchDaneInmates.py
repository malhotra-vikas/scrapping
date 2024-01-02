from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Specify the path to your WebDriver here if it's not in PATH
# For Chrome: webdriver.Chrome(executable_path='path/to/chromedriver')
# For Firefox: webdriver.Firefox(executable_path='path/to/geckodriver')
driver = webdriver.Chrome()

try:
    # Open the webpage
    driver.get("https://danesheriff.com/Residents")

    inmateURLList = ['https://danesheriff.com/Residents/detail/563074']
    page = 1
    collectURLs = False

    while collectURLs:
        # Wait for the page to load
        time.sleep(2)  # Adjust the sleep time as necessary

        # Find elements by XPath that contain the text 'Detail'
        elements = driver.find_elements(By.XPATH, "//*[text()='Detail']")

        for element in elements:
            currentURL = element.get_attribute('href')
            inmateURLList.append(currentURL)
            print(currentURL)

        # Try to navigate to the next page
        try:
            # Find the 'Next' button or pagination control and click it
            # Adjust the selector as per your website's structure
            next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")
            next_button.click()

            page += 1
            print(f"Moving to page {page}")
        except Exception as e:
            print("Last page reached or an error occurred:", e)
            break
    
    driver.quit()
    
    for inmateUrl in inmateURLList:
        driver = webdriver.Chrome()
        driver.get(inmateUrl)
        time.sleep(5)  # Adjust the sleep time as necessary

        # Find the table by its class
        table = driver.find_element(By.CLASS_NAME, "table-condensed")

        # Iterate through each row in the table
        for row in table.find_elements(By.TAG_NAME, "tr"):
            # Each 'td' in the row is a cell
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 1:  # Ensure there are at least 2 cells (label and value)
                label = cells[0].text  # The first cell is the label
                value = cells[1].text  # The second cell is the value
                print(label)
                print(value)
        
        # Find the accordion div
        accordion_div = driver.find_element(By.XPATH, "//div[@class='accordion mb-3' and @id='accordion1']")
        # Find all child elements that contain text within the accordion
        child_elements = accordion_div.find_elements(By.XPATH, ".//*[not(self::script or self::style)]")
        # Iterate over the child elements and print their text
        for element in child_elements:
            text = element.text.strip()
            if text:  # Print only if there is text
                print(text)

        driver.quit()
    
except:
    print("hi")
    driver.quit()