from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from time import sleep
from DatabaseManager import DatabaseManager
import tldextract


class Browser:

    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser = webdriver.Chrome(driver_path)
        self.db = DatabaseManager()
        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url
        ext = tldextract.extract(home_url)
        self.identifier = ext.domain
        self.db.add_new_webpage(self.identifier, {'home_url': home_url, 'login_url': login_url, 'register_url': register_url})
        # Credentials
        self.fields = ["email", "password", "name", "username"]
        self.credentials = {}
        self.credentials["email"] = "cookiehunterproject@gmail.com"
        self.credentials["password"] = "passwordRandom123!"
        self.credentials["name"] = "Janssen"
        self.credentials["username"] = "CookieHunter007"
        self.synonyms = {}
        self.synonyms["email"] = ['user_email', 'email', 'e_mail', 'useremail', 'userEmail', 'mail', 'uemail',
                               'User_email', 'Email', 'E_mail', 'Useremail', 'UserEmail', 'Mail', 'Uemail',
                               'User_email_address', 'Email_address', 'email_address', 'emailadress',
                               'UserEmailAddress', 'Email address', 'Email Address', 'EMAIL',
                               'MailAdress'
                               ]
        self.synonyms["password"] = ['user_password', 'password', 'pword', 'userpassword', 'userpwd', 'pwd', 'PWD',
                                  'u_password', 'passw', 'p_word', 'UserPassword', 'UserPwd', 'Pwd', 'pass', 'Password',
                                  'User Password', 'Passwd', 'ConfirmPasswd', 'Confirm Password', 'Confirm password',
                                  'onfirm Password', 'confirm password' , 'CnfrmPsswrd', 'ConfirmPwd', 'CnfrmPwd'
                                  ]
        self.synonyms["name"] = ['name_first', 'name', 'first_name', 'firstname', 'First_Name', 'f_name', 'firstName',
                              'User_efirstname', 'First_name', 'first_Name', 'NAME', 'F_NAME', 'FName',
                              'fname_', '_firstname', 'fullname', 'full_name', 'user_first_name', 'First Name', 'first name',
                              'nc_firstname', 'nc_firstname_required', 'First name', 'Name',

                              'last_name', 'lastname', 'last_Name', 'l_name', 'lastName',
                              'User_elastname', 'last_name', 'Last_Name', 'l_NAME', 'lName',
                              'lname_', '_lastname', 'user_last_name', 'Last Name', 'Last name', 'last name',
                              'nc_lastname', 'nc_lastname_required'
                              ]
        self.synonyms["username"] = ['username', 'uname', 'user_id', 'user_name', 'uName', 'u_Name', 'UserName',
                                  'user_name_new', 'new_username', 'user_username', 'user_username', 'user[username]',
                                  'Username', 'nc_username', 'nc_username_required', 'Gebruikersnaam'
                                  ]
        self.label_assignments = {}
        self.attribute_assignments = {}

    def filter_elements(self, element_list):
        iterator = filter(lambda element: element.is_displayed(), set(element_list))
        return list(iterator)

    def register(self):
        self.browser.get((self.register_url))
        creds_for_register = {}
        if self.cookie_box_oracle():
            self.cookie_accept()

        checks = self.browser.find_elements(By.XPATH, "//input[@type='checkbox']")
        for check in checks:
            check.click()

        for field in self.fields:
            self.label_finder(self.synonyms[field], field)
            self.generic_element_finder("//input[@type='{plc}']".format(plc = field), self.synonyms[field], field)

        for web_element, field in self.label_assignments.items():
            id_value = web_element.get_attribute("for")
            if id_value is not None:
                for input_element in self.attribute_assignments.keys():
                    if input_element.get_attribute("value") == "":
                        id_from_element = input_element.get_attribute("id")
                        if id_from_element is not None and id_value in id_from_element:
                            self.attribute_assignments[input_element] = field
                            input_element.send_keys(self.credentials[field])
                            creds_for_register[field] = self.credentials[field]

        for web_element, field in self.attribute_assignments.items():
            if web_element.get_attribute("value") == "":
                web_element.send_keys(self.credentials[field])
                creds_for_register[field] = self.credentials[field]

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

        # TODO: add emailVerifier,

        self.login()
        if self.login_oracle():
            self.fill_database(able_to_fill_register=True, able_to_fill_login=True, registered=True, captcha=False,
                               creds_for_register=creds_for_register)

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

        # sleep(10)
        # First check if there is indeed a cookie popup, otherwise you don't know what button you are clicking
        for el in cookie_elements:
            try:
                self.browser.find_element_by_xpath(f"//*[contains(text(), {el})]")
                return True
            except Exception as e:
                print(e)
        return False

    def cookie_accept(self):

        # text which could be inside cookie accept buttons:
        cookie_accept_elements = [ 'bevestig', 'Bevestig', 'confirm', 'Confirm','Accepteer',
                                  'accepteer',  'Accept','accept', 'cookies', 'Cookies', 'keuze', 'choice']

        for el in cookie_accept_elements:
            try:
                accept_button_options = self.browser.find_elements_by_xpath(f"//button[contains(text(), {el})]")
                for b in accept_button_options:
                    try:
                        b.click()
                        self.browser.get((self.register_url))
                        return
                    except Exception as e:
                        pass
            except Exception as e:
                pass


    def login(self):
        self.browser.get((self.login_url))

        if self.cookie_box_oracle():
            self.cookie_accept()
        for field in self.fields:
            self.label_finder(self.synonyms[field], field)
            self.generic_element_finder("//input[@type='{plc}']".format(plc=field), self.synonyms[field], field)
        for web_element, field in self.label_assignments.items():
            id_value = web_element.get_attribute("for")
            if id_value is not None:
                for input_element in self.attribute_assignments.keys():
                    if input_element.get_attribute("value") == "":
                        id_from_element = input_element.get_attribute("id")
                        if id_from_element is not None and id_value in id_from_element:
                            self.attribute_assignments[input_element] = field
                            input_element.send_keys(self.credentials[field])

        for web_element, field in self.attribute_assignments.items():
            if web_element.get_attribute("value") == "":
                web_element.send_keys(self.credentials[field])

        print("form filling complete")

        # pwd.submit()

    def login_oracle(self):
        logged_in = self.name in self.browser.page_source
        return logged_in

    def refresh(self):
        self.browser.refresh()

    def generic_element_finder(self, x_path_text, text_list, type_string):
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

                placeholder = "//input[@aria-label=\"{plc}\"]".format(plc = text)
                element = self.browser.find_elements(By.XPATH, placeholder)
                element_list = element_list + element

        element_list = self.filter_elements(element_list)
        for web_element in element_list:
            self.attribute_assignments[web_element] = type_string

    def label_finder(self, text_list, type_string):
        element_list = []
        label_xpath = "//label[contains(text(),'{el}')]"
        for text in text_list:
                element = self.browser.find_elements(By.XPATH, label_xpath.format(el=text))
                element_list = element_list + element
        element_list = self.filter_elements(element_list)
        for web_element in element_list:
            self.label_assignments[web_element] = type_string
            id_value = web_element.get_attribute("for")
            if id_value is not None and id_value is not "":
                self.synonyms[type_string].append(id_value)

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
