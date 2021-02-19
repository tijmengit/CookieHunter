from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


if __name__ == "__main__":
    PATH = "C:\cookie_test\chromedriver"
    browser = webdriver.Chrome(PATH)

    browser.get(('https://www.mentimeter.com/signup'))
    email = browser.find_element_by_id('email')
    email.send_keys("pegoge3882@mayhco.com")
    pwd = browser.find_element_by_id('password')
    pwd.send_keys("randompassword123!")
    pwd = browser.find_element_by_id('password')
    button = browser.findElement(By.xpath("//button[text()='Sign up']")).click();
    button.click()