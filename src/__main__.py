from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
from CookieHunter.src.Browser import *

if __name__ == "__main__":
    home_url = ""
    login_url = "https://www.goodreads.com/user/sign_in"
    register_url = "https://www.goodreads.com/user/sign_up"
    PATH = "/usr/local/sbin/chromedriver"
    browser = Browser(home_url=home_url, login_url=login_url, register_url=register_url, driver_path=PATH)
    # browser.register()
    browser.login()
    print("Login oracle says: ", browser.login_oracle())


    # with open('../data/sites.json') as sites_file:
    #     sites = json.load(sites_file)
    #     for site in sites:
    #         browser = Browser(home_url=site['home_url'], login_url=site['login_url'], register_url=site['register_url'], driver_path=PATH)
    #         browser.register()



