from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options

from time import sleep
from CookieHunter.src.DatabaseManager import DatabaseManager
from CookieHunter.src.EmailVerifier import EmailVerifier
import tldextract


class Browser:

    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser_options = Options()
        self.prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.popups": 2,
            "translate_whitelists": self.language_whitelist(),
            "translate": {"enabled": "true"}
        }
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser = webdriver.Chrome(driver_path)
        self.db = DatabaseManager()
        self.emailVerifier = EmailVerifier()
        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url
        ext = tldextract.extract(home_url)
        self.identifier = ext.domain
        self.db.add_new_webpage(self.identifier, {'home_url': home_url, 'login_url': login_url, 'register_url': register_url})
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
        self.cookie_accept_synonyms = [ 'Accept','accept','ACCEPT','bevestig', 'Bevestig', 'confirm', 'Confirm','Accepteer',
                                  'accepteer','ACCEPTEER',  'keuze', 'choice', 'accept all cookies',
                                        'Accept all cookies','Accept All Cookies', 'I Accept', "I Consent"]


    def filter_elements(self, element_list):
        iterator = filter(lambda element: element.is_displayed(), set(element_list))
        return list(iterator)

    def register(self):
        self.browser.get((self.register_url))
        creds_for_register = {}
        if self.cookie_box_oracle():
            self.cookie_accept()

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
        # button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
        # button.click()
        # name.submit()
        # button = browser.findElement(By.xpath("//button[text()='Sign up']")).click();
        # button.click()

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

    def language_whitelist(self):
        languages = ["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "ceb", "co", "cs", "cy", "da", "de",
                     "el", "en",
                     "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl", "gu", "ha", "haw", "hi",
                     "hmn", "hr",
                     "ht", "hu", "hy", "id", "ig", "is", "it", "iw", "ja", "jv", "ka", "kk", "km", "kn", "ko", "ku",
                     "ky",
                     "la", "lb", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl",
                     "no",
                     "ny", "or", "pa", "pl", "ps", "pt", "ro", "ru", "rw", "sd", "si", "sk", "sl", "sm", "sn", "so",
                     "sq",
                     "sr", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "ug", "uk", "ur",
                     "uz",
                     "vi", "xh", "yi", "yo", "zh-CN", "zh-TW", "zu"]
        dict = {}
        for l in languages:
            dict[l] = "en"
        return dict
