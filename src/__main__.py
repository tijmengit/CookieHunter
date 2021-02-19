from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
class BrowserLogin:


    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser = webdriver.Chrome(driver_path)
        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url

        # Credentials
        self.email_address = "cookiehunterproject@gmail.com"
        self.pwd = "passwordRandom123!"
        self.name = "Cookie Hunter"


    def register(self):
        self.browser.get((self.register_url))
        email = self.email_el()
        pwd = self.pwd_el()
        name = self.name_el()

        email.send_keys(self.email_address)
        pwd.send_keys(self.pwd)
        name.send_keys(self.name)

        # name.submit()
        # button = browser.findElement(By.xpath("//button[text()='Sign up']")).click();
        # button.click()

    def email_el(self):
        email = None
        try:
            email = self.browser.find_element_by_id('email')
        except Exception as e:
            print(e)
        return email

    def pwd_el(self):
        pwd = None
        try:
            pwd = self.browser.find_element_by_id('password')
        except Exception as e:
            print(e)
        return pwd

    def name_el(self):
        name = None
        try:
            name = self.browser.find_element_by_id('name')
        except Exception as e:
            print(e)
        return name


if __name__ == "__main__":
    home_url = ""
    login_url = ""
    register_url = 'https://www.mentimeter.com/signup'
    PATH = "/usr/local/sbin/chromedriver"
    # browser = BrowserLogin(home_url=home_url, login_url=login_url, register_url=register_url, driver_path=PATH)
    # browser.register()
    with open('data/sites.json') as sites_file:
        sites = json.load(sites_file)
        for site in sites:
            browser = BrowserLogin(home_url=site['home_url'], login_url=site['login_url'], register_url=site['register_url'], driver_path=PATH)
            browser.register()



