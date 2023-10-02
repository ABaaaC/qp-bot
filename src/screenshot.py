from selenium import webdriver
from selenium.webdriver.common.by import By

def generate_screenshot(lottery_number):
    # Setup Selenium with headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=400x400")
    
    # Path to the ChromeDriver executable
    # chrome_driver_path = "path/to/chromedriver"
    
    # Initialize the browser
    # browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
    browser = webdriver.Chrome(options=chrome_options)
    
    # Open the HTML file
    browser.get("file:///Users/sabukhovich/Documents/crypto/gpt/qp-bot/lottery_web/index.html")
    
    # Replace the lottery number
    element = browser.find_element(By.CLASS_NAME, "lototron__pink")
    # element = browser.find_element_by_class_name("lototron__pink")
    browser.execute_script(f"arguments[0].innerText = '{lottery_number}'", element)
    
    # Capture a screenshot
    # screenshot_path = f"lottery_number_{lottery_number}.png"
    screenshot_path = f"screenshots/lottery_number_{lottery_number}.png"
    browser.save_screenshot(screenshot_path)
    
    # Close the browser
    browser.quit()
    
    return screenshot_path

# Example usage
if __name__ == '__main__':
    # for i in range(1, 401):
    #     screenshot_path = generate_screenshot(i)
    #     print(f"Screenshot saved at {screenshot_path}")
    screenshot_path = generate_screenshot(76)
    print(f"Screenshot saved at {screenshot_path}")

