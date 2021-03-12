from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options

from time import sleep
from CookieHunter.src.DatabaseManager import DatabaseManager
from CookieHunter.src.EmailVerifier import EmailVerifier
from CookieHunter.src.Helper import *
import tldextract
import urllib.parse as urlparse
from bs4 import BeautifulSoup as BS

class Browser:

    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser_options = Options()
        self.prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.popups": 2,
            "translate_whitelists": language_whitelist(),
            "translate": {"enabled": "true"}
        }
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser = webdriver.Chrome(driver_path, options=self.browser_options)
        self.browser.set_page_load_timeout(10)
        # self.db = DatabaseManager()
        self.emailVerifier = EmailVerifier()
        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url
        ext = tldextract.extract(home_url)
        self.identifier = ext.domain
        # self.db.add_new_webpage(self.identifier, {'home_url': home_url, 'login_url': login_url, 'register_url': register_url})
        # Credentials
        self.email_address = f'cookiehunterproject+{self.identifier}@gmail.com'
        print(self.email_address)

        self.pwd = "passwordRandom123!"
        self.name = "Janssen"
        self.username = "CookieHunter007"
        self.email_synonyms = ['user_email', 'email', 'e_mail', 'useremail', 'userEmail', 'mail', 'uemail',
                               'User_email', 'Email', 'E_mail', 'Useremail', 'UserEmail', 'Mail', 'Uemail',
                               'User_email_address', 'Email_address', 'email_address', 'emailadress',
                               'UserEmailAddress', 'Email address', 'Email Address', 'EMAIL',
                               'MailAdress'
                               ]
        self.password_synonyms = ['user_password', 'password', 'pword', 'userpassword', 'userpwd', 'pwd', 'PWD',
                                  'u_password', 'passw', 'p_word', 'UserPassword', 'UserPwd', 'Pwd', 'pass', 'Password',
                                  'User Password', 'Passwd', 'ConfirmPasswd', 'Confirm Password', 'Confirm password',
                                  'onfirm Password', 'confirm password' , 'CnfrmPsswrd', 'ConfirmPwd', 'CnfrmPwd'
                                  ]
        self.name_synonyms = ['name_first', 'name', 'first_name', 'firstname', 'First_Name', 'f_name', 'firstName',
                              'User_efirstname', 'First_name', 'first_Name', 'NAME', 'F_NAME', 'FName',
                              'fname_', '_firstname', 'fullname', 'full_name', 'user_first_name', 'First Name', 'first name',
                              'nc_firstname', 'nc_firstname_required', 'First name',

                              'last_name', 'lastname', 'last_Name', 'l_name', 'lastName',
                              'User_elastname', 'last_name', 'Last_Name', 'l_NAME', 'lName',
                              'lname_', '_lastname', 'user_last_name', 'Last Name', 'Last name', 'last name',
                              'nc_lastname', 'nc_lastname_required'

                              ]
        self.username_synonyms = ['username', 'uname', 'user_id', 'user_name', 'uName', 'u_Name', 'UserName',
                                  'user_name_new', 'new_username', 'user_username', 'user_username', 'user[username]',
                                  'Username', 'nc_username', 'nc_username_required', 'Gebruikersnaam'
                                  ]
        self.cookie_accept_synonyms = [ 'accept','bevestig', 'confirm', 'accepteer','keuze', 'choice', 'accept all cookies',
                                         'I accept', "I Consent"]
        create_synonyms(self.cookie_accept_synonyms)

        self.sign_up_synonyms = ['register','registration', 'sign up','signup','createuser', 'create user']
        create_synonyms(self.sign_up_synonyms)

        self.login_synonyms = ['login', 'log-in', 'log in']
        create_synonyms(self.login_synonyms)


    def filter_elements(self, element_list):
        iterator = filter(lambda element: element.is_displayed(), set(element_list))
        return list(iterator)

    def login(self):
        self.browser.get((self.login_url))
        email = self.generic_element_finder("//input[@type='email']", self.email_synonyms)
        for field in email:
            if field.get_attribute("value") == "":
                field.send_keys(self.email_address)
            else:
                print("Field already filled by others")

        username = self.generic_element_finder("//input[@type='username']", self.username_synonyms)
        for field in username:
            if field.get_attribute("value") == "":
                field.send_keys(self.username)
            else:
                print("Field already filled by others")

        pwd = self.generic_element_finder("//input[@type='password']", self.password_synonyms)
        for field in pwd:
            if field.get_attribute("value") == "":
                field.send_keys(self.pwd)
            else:
                print("Field already filled by others")

        pwd.submit()

    def register(self):
        if not self.register_url:
            self.browser.get(self.home_url)
        else:
            self.browser.get(self.register_url)
        creds_for_register = {}
        if self.cookie_box_oracle():
            self.cookie_accept()
        if not self.register_url:
            self.navigate_to_register()

        # login_form = self.browser.find_element_by_xpath("//form[1]")
        checks = self.browser.find_elements(By.XPATH, "//input[@type='checkbox']")
        for check in checks:
            check.click()

        email = self.generic_element_finder("//input[@type='email']", self.email_synonyms)
        for field in email:
            if field.get_attribute("value") == "":
                field.send_keys(self.email_address)
                creds_for_register['email'] = self.email_address
            else:
                print("Field already filled by others")

        username = self.generic_element_finder("//input[@type='username']", self.username_synonyms)
        for field in username:
            if field.get_attribute("value") == "":
                field.send_keys(self.username)
                creds_for_register['username'] = self.username
            else:
                print("Field already filled by others")

        pwd = self.generic_element_finder("//input[@type='password']", self.password_synonyms)
        for field in pwd:
            if field.get_attribute("value") == "":
                field.send_keys(self.pwd)
                creds_for_register['pwd'] = self.pwd
            else:
                print("Field already filled by others")

        name = self.generic_element_finder("//input[@type='name']", self.name_synonyms)
        for field in name:
            if field.get_attribute("value") == "":
                field.send_keys(self.name)
                creds_for_register['name'] = self.name
            else:
                print("Field already filled by others")

        print("form filling complete")
        sleep(10)

        # Comment this out to submit registration:
        # self.submit_registration(name, creds_for_register)

    def submit_registration(self, el, creds_for_register):
        el.submit()

        msgId, link = self.verifyEmail()
        if msgId:
            self.browser.get(link)
            sleep(3)
            self.browser.close()
            self.db.update_web_page(self.identifier, {'verified': True})
            self.emailVerifier.messageRead(msgId)

        self.login()
        if self.login_oracle():
            self.fill_database(able_to_fill_register=True, able_to_fill_login=True, registered=True, captcha=False,
                               creds_for_register=creds_for_register)

    def verifyEmail(self, max_tries=6) -> Tuple[Optional[str], Optional[str]]:
        tries = 1
        while tries <= max_tries:
            delay = 2**tries
            sleep(delay)
            msgId, link = self.emailVerifier.getUnreadEmailLinks(self.identifier, days=30)
            if link:
                return msgId, link

            tries += 1
        return None, None

    def fill_database(self, able_to_fill_register, able_to_fill_login, registered, captcha, creds_for_register):
        data = {}
        data['register_data'] = creds_for_register
        data['able_to_fill_register'] = able_to_fill_register
        data['able_to_fill_login'] = able_to_fill_login
        data['registered'] = registered
        data['captcha'] = captcha
        self.db.update_web_page(self.identifier, data)



    def cookie_box_oracle(self):
        '''
        Function to check for a cookie box, which asks for consent
        :return: Cookie box present
        '''
        cookie_elements = ['cookieContainer', 'cookieOverlay', 'cookieAcceptForm']

        sleep(5)
        # First check if there is indeed a cookie popup, otherwise you don't know what button you are clicking
        for el in cookie_elements:
            try:
                self.browser.find_element_by_xpath(f"//*[contains(text(), {el})]")
                return True
            except Exception as e:
                print(e)
        return False

    def cookie_accept(self):
        accept_button_options = self.generic_buttons(self.cookie_accept_synonyms)
        for b in accept_button_options:
            try:
                b.click()
                self.browser.get((self.home_url))
                return
            except Exception as e:
                pass


    def navigate_to_register(self):
        url = self.get_sitemap(self.sign_up_synonyms)
        if len(url)>0:
            self.register_url = url[0]
            self.browser.get((self.register_url))

    def identify_form(self):
        pwd_fields = self.generic_input_element_finder(self.password_synonyms)
        if len(pwd_fields) > 1:
            return 'register'
        name = self.generic_element_finder("//input[@type='name']", self.name_synonyms)
        if len(name) >0:
            return 'register'
        if len(pwd_fields) == 1:
            return 'login'
        return 'contact'

    def get_sitemap(self, keywords):
        depth = 2
        limit = 50

        queue = [(self.home_url, 0)]
        found = []

        base = urlparse.urlparse(self.home_url).netloc
        handled = []

        while queue:
            page = queue.pop(0)
            self.browser.get(page[0])
            handled.append(page)
            soup = BS(self.browser.page_source, 'html.parser')

            for link in soup.select('body a')[:limit]:
                full_link = urlparse.urljoin(self.home_url, link.get('href'))
                parsed_link = urlparse.urlparse(full_link)
                path = parsed_link.path.split('/')
                elem = path[1] if len(path) >= 2 else ''
                if elem == 'signup':
                    print(elem)
                # create clean link without queries, parameters or fragments
                clean_link = f'{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}'

                if elem in keywords \
                        and clean_link not in found:
                    found.append(clean_link)

                if page[1] < depth\
                        and clean_link not in handled \
                        and clean_link not in found\
                        and elem in self.login_synonyms:
                    queue.append((clean_link, page[1] + 1))
                    queue = sorted(queue, key=lambda x: x[1])

        return found

    def login_oracle(self):
        logged_in = self.name in self.browser.page_source
        return logged_in

    def refresh(self):
        self.browser.refresh()

    def generic_element_finder(self, x_path_text, text_list):
        element_list = []
        element = self.browser.find_elements(By.XPATH, x_path_text)
        element_list = element_list + element

        for text in text_list:
                element = self.browser.find_elements(By.NAME, text)
                element_list = element_list + element

                element = self.browser.find_elements(By.TAG_NAME, text)
                element_list = element_list + element

                element = self.browser.find_elements(By.ID, text)
                element_list = element_list + element

                placeholder = "//input[@placeholder=\"{plc}\"]".format(plc = text)
                element = self.browser.find_elements(By.XPATH, placeholder)
                element_list = element_list + element

                placeholder = "//input[@placeholder=\'{plc}\']".format(plc = text)
                element = self.browser.find_elements(By.XPATH, placeholder)
                element_list = element_list + element

        return self.filter_elements(element_list)


    def generic_input_element_finder(self, text_list):
        '''
        This function returns generic input elements.
        !! This will not work for input values for "name" since it will also match username input type
        :param text_list:
        :return: input element
        '''
        element_set = set()
        attr = ['@id', '@name', '@placeholder']
        for syn in text_list:
            for a in attr:
                if ' ' in syn:
                    continue
                elements = self.browser.find_elements_by_xpath(f'//input[contains({a}, {syn})]')
                for element in elements:
                    element_set.add(element)
        return self.filter_elements(list(element_set))

    def generic_buttons(self, text_list):
        button_set = set()
        for syn in text_list:
            # x_paths = [f'//button[text()={syn}]', f'//a[contains(text(), {syn})]',  f'//div[contains(text(), {syn})]']
            x_paths = ['//button[text()="'+syn+'"]']
            for path in x_paths:
                buttons = self.browser.find_elements_by_xpath(path)
                for b in buttons:
                    button_set.add(b)
        return self.filter_elements(list(button_set))

    def get_cookies(self):
        return self.browser.get_cookies()

    def set_cookies(self, cookies):
        return

    def add_cookie(self, cookie):
        self.browser.add_cookie(cookie)

    def delete_cookies(self, cookies=[]):
        if not cookies:
            self.browser.delete_all_cookies()
        else:
            for cookie in cookies:
                self.delete_cookie(cookie)

    def delete_cookie(self, cookie):
        if type(cookie) is dict:
            cookie = cookie['name']
        self.browser.delete_cookie(cookie)

    def get_driver(self):
        return self.browser

    def close(self):
        self.browser.quit()



