from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
class Browser:

    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser = webdriver.Chrome(driver_path)
        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url

        # Credentials
        self.email_address = "cookiehunterproject@gmail.com"
        self.pwd = "passwordRandom123!"
        self.name = "Jan Janssen"
        self.username = "CookieHunter007"
        self.email_synonyms = ['user_email', 'email', 'e_mail', 'useremail', 'userEmail', 'mail', 'uemail',
                         'User_email', 'Email', 'E_mail', 'Useremail', 'UserEmail', 'Mail', 'Uemail',
                         'User_email_address', 'Email_address', 'email_address', 'emailadress', 'UserEmailAddress',
                         'MailAdress'
                         ]
        self.password_synonyms = ['user_password', 'password', 'pword', 'userpassword', 'userpwd', 'pwd', 'PWD',
                         'u_password', 'passw', 'p_word', 'UserPassword', 'UserPwd', 'Pwd', 'pass',
                         ]
        self.name_synonyms = ['name_first', 'name', 'first_name', 'firstname', 'First_Name', 'f_name', 'firstName',
                               'User_efirstname', 'First_name', 'first_Name', 'NAME', 'F_NAME', 'FName',
                               'fname_', '_firstname', 'fullname', 'full_name','user_first_name'
                               ]
        self.username_synonyms = ['username', 'uname', 'user_id', 'user_name', 'uName', 'u_Name', 'UserName',
                               'user_name_new', 'new_username', 'user_username', 'user_username', 'user[username]'
                               ]

    def register(self):
        self.browser.get((self.register_url))
        # login_form = self.browser.find_element_by_xpath("//form[1]")
        checks = self.browser.find_elements(By.XPATH, "//input[@type='checkbox']")
        for check in checks:
            check.click()

        email = self.generic_element_finder("//input[@type='email']", self.email_synonyms)
        if email is not None:
            email.send_keys(self.email_address)

        pwd = self.generic_element_finder("//input[@type='password']", self.password_synonyms)
        if pwd is not None:
            pwd.send_keys(self.pwd)

        name = self.generic_element_finder("//input[@type='name']", self.name_synonyms)
        if name is not None:
            name.send_keys(self.name)

        username = self.generic_element_finder("//input[@type='username']", self.username_synonyms)
        if username is not None:
            username.send_keys(self.username)

        # button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
        # button.click()
        print("form filling complete")
        # name.submit()
        # button = browser.findElement(By.xpath("//button[text()='Sign up']")).click();
        # button.click()

    def login(self):
        self.browser.get((self.login_url))
        email = self.generic_element_finder("//input[@type='email']", self.email_synonyms)
        if email is not None:
            email.send_keys(self.email_address)
        pwd = self.generic_element_finder("//input[@type='password']", self.password_synonyms)
        if pwd is not None:
            pwd.send_keys(self.pwd)

        pwd.submit()

    def login_oracle(self):
        logged_in = self.name in self.browser.page_source
        return logged_in

    def generic_element_finder(self, x_path_text, text_list):
        element = None
        try:
            element = self.browser.find_element(By.XPATH, x_path_text)
        except Exception as e:
            pass
        for text in text_list:
            try:
                element = self.browser.find_element(By.NAME, text)
            except Exception as e:
                pass
                # print(e)
            try:
                element = self.browser.find_element(By.TAG_NAME, text)
            except Exception as e:
                pass
                # print(e)
            try:
                element = self.browser.find_element(By.ID, text)
            except Exception as e:
                pass

        return element


if __name__ == "__main__":
    home_url = ""
    login_url = "https://www.goodreads.com/user/sign_in"
    register_url = "https://www.goodreads.com/user/sign_up"
    PATH = "/usr/local/sbin/chromedriver"
    browser = Browser(home_url=home_url, login_url=login_url, register_url=register_url, driver_path=PATH)
    # browser.register()
    browser.login()
    browser.login_oracle()
    # with open('../data/sites.json') as sites_file:
    #     sites = json.load(sites_file)
    #     for site in sites:
    #         browser = Browser(home_url=site['home_url'], login_url=site['login_url'], register_url=site['register_url'], driver_path=PATH)
    #         browser.register()



