from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options

from time import sleep
from src.DatabaseManager import DatabaseManager
from src.EmailVerifier import EmailVerifier
from src.Helper import *
import tldextract
import urllib.parse as urlparse
from bs4 import BeautifulSoup as BS

from selenium.webdriver.common.keys import Keys
from src.Helper import create_synonyms


class Browser:

    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser_options = Options()
        self.prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "translate_whitelists": language_whitelist(),
            "translate": {"enabled": "true"}
        }
        self.browser_options.add_experimental_option("prefs", self.prefs)
        self.browser = webdriver.Chrome(driver_path, options=self.browser_options)
        self.browser.set_page_load_timeout(10)
        self.db = DatabaseManager()
        self.emailVerifier = EmailVerifier()
        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url
        ext = tldextract.extract(home_url)
        self.identifier = ext.domain+"115"
        self.db.add_new_webpage(self.identifier, {'home_url': home_url, 'login_url': login_url, 'register_url': register_url})
        # Credentials
        self.fields = ["email", "password", "name", "username"]
        self.credentials = {}
        self.credentials["email"] = f'cookiehunterproject+{self.identifier}@gmail.com'
        self.credentials["password"] = "passwordRandom123!"
        self.credentials["name"] = "Janssen"
        self.credentials["username"] = "CookieHunter007"
        self.synonyms = {}
        self.synonyms["email"] = ['user_email', 'email', 'e_mail', 'useremail', 'userEmail', 'mail', 'uemail',
                                  'User_email', 'E_mail' , 'UserEmail', 'Mail', 'Uemail',
                                  'User_email_address', 'Email_address', 'email_address', 'emailadress',
                                  'UserEmailAddress', 'Email address', 'Email Address', 'EMAIL',
                                  'MailAdress', 'User Email', 'E-mail Address', 'e-mail address', 'Email address',
                                  'User Email Address', 'User email address'
                                  ]
        self.synonyms["password"] = ['user_password', 'password', 'pword', 'userpassword', 'userpwd', 'pwd', 'PWD',
                                     'u_password', 'passw', 'p_word', 'UserPassword', 'UserPwd', 'Pwd', 'pass',
                                     'Password',
                                     'User Password', 'Passwd', 'ConfirmPasswd', 'Confirm Password', 'Confirm password',
                                     'onfirm Password', 'confirm password', 'CnfrmPsswrd', 'ConfirmPwd', 'CnfrmPwd',
                                     'Re-enter Password', 'Password Confirm'
                                     ]
        self.synonyms["name"] = ['name_first', 'name', 'first_name', 'firstname', 'First_Name', 'f_name', 'firstName',
                                 'User_efirstname', 'First_name', 'first_Name', 'NAME', 'F_NAME', 'FName',
                                 'fname_', '_firstname', 'fullname', 'full_name', 'user_first_name', 'First Name',
                                 'first name',
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
        self.synonyms['cookie-accept'] = [ 'accept', 'confirm', 'choice', 'accept all cookies',
                                         'I accept', "I Consent", "allow all cookies"]

        self.synonyms['register'] = ['register','registration', 'sign up','signup','createuser', 'create user']

        self.synonyms['login'] = ['login', 'log-in', 'log in']

        self.label_assignments = {}
        self.attribute_assignments = {}

        create_synonyms(self.synonyms['cookie-accept'])
        create_synonyms(self.synonyms['register'])
        create_synonyms(self.synonyms['login'])

    def filter_elements(self, element_list):
        iterator = filter(lambda element: element.is_displayed(), set(element_list))
        return list(iterator)

    def register(self):
        if not self.register_url:
            url = self.home_url
            self.browser.get(self.home_url)
        else:
            url = self.register_url
            self.browser.get(self.register_url)

        if self.cookie_box_oracle():
            self.cookie_accept(url)
        if not self.register_url:
            if self.navigate_to_register():
                print('Registration url found')
            elif self.identify_form() == 'register':
                print('Registration form on homepage')
            else:
                print('No registration url found')
                return

        checks = self.browser.find_elements(By.XPATH, "//input[@type='checkbox']")
        for check in self.filter_elements(checks):
            check.click()

        creds_for_register = self.fill_attributes()

        # Comment this out to submit registration:
        if len(creds_for_register) > 0:
            print("At least one input field has been filled")
            return self.submit_registration(creds_for_register)
        else:
            print("No submission done")
            return False

    def login(self):

        if not self.login_url:
            url = self.home_url
            self.browser.get(self.home_url)
        else:
            url = self.login_url
            self.browser.get(self.login_url)

        if self.cookie_box_oracle():
            self.cookie_accept(url)

        if not self.login_url:
            self.navigate_to_login()

        creds_for_login = self.fill_attributes()
        print("form filling complete")
        if len(creds_for_login) > 0:
            for web_element, field in self.attribute_assignments.items():
                try:
                    web_element.submit()
                    print('Form submitted')
                    break
                except Exception as e:
                    print(e)


    def fill_attributes(self):
        creds_for_register = {}
        self.attribute_assignments = {}
        self.label_assignments = {}
        # label and input field searching done here
        for field in self.fields:
            self.label_finder(self.synonyms[field], field)
            self.generic_element_finder("//input[@type='{plc}']".format(plc=field), self.synonyms[field], field)

        # filling in the elements depending on their labels here, we iterate through labels and look for the input fields to match with labels for attributes
        for web_element, field in self.label_assignments.items():
            id_value = web_element.get_attribute("for")
            # Check for the labels without any for attribute
            if id_value is not None:
                for input_element in self.attribute_assignments.keys():
                    if input_element.get_attribute("value") == "":
                        id_from_element = input_element.get_attribute("id")
                        # this is where we match an element based on the label for attribute and the id of the element
                        if id_from_element is not None and id_value in id_from_element:
                            self.attribute_assignments[input_element] = field
                            input_element.send_keys(self.credentials[field])
                            creds_for_register[field] = self.credentials[field]

        for web_element, field in self.attribute_assignments.items():
            if web_element.get_attribute("value") == "":
                web_element.send_keys(self.credentials[field])
                creds_for_register[field] = self.credentials[field]

        return creds_for_register

    def submit_registration(self, creds_for_register):
        for web_element, field in self.attribute_assignments.items():
            try:
                web_element.submit()
                print('Form submitted')
                web_element.send_keys(Keys.ENTER)
                break
            except Exception as e:
                print('FORM NOT SUBMITTED')
                print(e)

        email_received = False
        msgId, link = self.verifyEmail(max_tries=3)
        if msgId:
            print("Verification mail received")
            email_received = True
            self.browser.get(link)
            sleep(3)
            self.browser.close()
            self.db.update_web_page(self.identifier, {'verified': True})
            self.emailVerifier.messageRead(msgId)

        if email_received or self.registration_oracle(creds_for_register):
            print(f'registration successful, adding {self.home_url} to database')
            self.fill_database(able_to_fill_register=True, able_to_fill_login=True, registered=True, captcha=False,
                               creds_for_register=creds_for_register)
            return True
        else:
            return False


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

    def cookie_accept(self, url):
        accept_button_options = self.generic_buttons(self.synonyms['cookie-accept'])
        for b in accept_button_options:
            try:
                b.click()
                self.browser.get(url)
                return
            except Exception as e:
                pass

    def navigate_to_register(self):
        url = self.get_sitemap(self.synonyms['register'])
        if len(url)>0:
            self.register_url = url[0]
            self.browser.get((self.register_url))
            return True
        else:
            return False

    def navigate_to_login(self):
        url = self.get_sitemap(self.synonyms['login'])
        if len(url)>0:
            self.login_url = url[0]
            self.browser.get((self.login_url))

    def identify_form(self):
        pwd_fields = 0
        name_fields = 0
        input_fields = 0
        for web_element, field in self.attribute_assignments.items():
            if web_element.get_attribute("value") == "" or len(web_element.get_attribute("value"))>1:
                input_fields += 1
                if field == 'password':
                    pwd_fields += 1
                elif field == 'name':
                    name_fields += 1
        if pwd_fields > 1:
            return 'register'
        if name_fields >0:
            return 'register'
        if pwd_fields == 1:
            return 'login'
        if input_fields ==0:
            return 'no form'
        return 'unknown'

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
                # create clean link without queries, parameters or fragments
                clean_link = f'{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}'

                if elem in keywords \
                        and clean_link not in found:
                    found.append(clean_link)

                if page[1] < depth\
                        and clean_link not in handled \
                        and clean_link not in found\
                        and elem in self.synonyms['login']:
                    queue.append((clean_link, page[1] + 1))
                    queue = sorted(queue, key=lambda x: x[1])

        return found

    def login_oracle(self):
        '''
        Step 1: Refetch page and check whether submitted form is still there
        If False: We are logged in
        Else: (Follow)
        Step 2: Check if Account Identifiers are present + Logout Button
        If True: We are logged in
        Else: We are not logged in
        Step 3: Check false positves
        [send HTTP request without any cookies and consult login oracle once again]
        '''
        logged_in = False
        second_step = False
        self.browser.get((self.login_url))

        for field in self.fields:
            elements = self.generic_element_finder("//input[@type='{plc}']".format(plc=field), self.synonyms[field], field)
            if not elements:
                logged_in = True
            else:
                logged_in = False       #if one element is not empty --> go to step 2
                second_step = True
                break

        if second_step:
            self.browser.get(self.home_url)
            for value in self.credentials.values():
                if value in self.browser.page_source:
                    logged_in = True

        print("Login Oracle - Logged in: ", logged_in)
        return logged_in


    def login_oracle_help(self, website):
        self.browser.execute_script(f'''window.open("{website}","_blank");''')
        self.browser.switch_to.window(self.browser.window_handles[1])

    def registration_oracle(self, creds_for_register):
        '''
        3 checks for registration oracle:
        1. visit registration url and check if input fields are still there
        2. visit homepage and check for credentials passed to registration
        3. attempt to login
        '''
        # 1. visit registration url and check for input fields used to register
        try:
            self.browser.get(self.register_url)
        except Exception as e:
            pass

        self.fill_attributes()
        if self.identify_form() == 'no form':
            return True

        # 2. check for creds on homepage
        self.browser.get(self.home_url)
        for cred in creds_for_register.values():
            if cred in self.browser.page_source:
                print('Login successful for ' + self.home_url)
                return True

        # 3. attempt login
        self.login()
        if self.login_oracle():
            print('Login successful for ' + self.home_url)
            return True
        print('Registration possibly unsuccessful for ' + self.home_url)
        return False


    def refresh(self):
        self.browser.refresh()

    def generic_element_finder(self, x_path_text, text_list, type_string):
        '''
        Function that finds form elements that will be filled
        :param x_path_text: "//input[@type='{plc}']" finding inputs based on their types
        :param text_list: manually curated keyword list
        :param type_string: what type of credentials we are filling
        :return: None
        '''
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

            placeholder = "//input[@placeholder=\"{plc}\"]".format(plc=text)
            element = self.browser.find_elements(By.XPATH, placeholder)
            element_list = element_list + element

            placeholder = "//input[@aria-label=\"{plc}\"]".format(plc=text)
            element = self.browser.find_elements(By.XPATH, placeholder)
            element_list = element_list + element

        element_list = self.filter_elements(element_list)
        # After finding the elements and filtering for duplicates and hidden elements, we put them in the attribute_assignments dictionary with the value being the type of credentials we are filling
        for web_element in element_list:
            self.attribute_assignments[web_element] = type_string
        return element_list

    def label_finder(self, text_list, type_string):
        '''
        Function that finds label elements
        :param text_list: manually curated keyword list
        :param type_string: what type of credentials we are filling
        :return: None
        '''
        element_list = []
        label_xpath = "//label[contains(text(),'{el}')]"
        label_span_xpath = "//label/descendant::span[contains(text(),'{el}')]"
        for text in text_list:
            element = self.browser.find_elements(By.XPATH, label_xpath.format(el=text))
            element_list = element_list + element
            inner_span = self.browser.find_elements(By.XPATH, label_span_xpath.format(el=text))
            for span_element in inner_span:
                element = span_element.find_elements(By.XPATH, ("./.."))
                element_list = element_list + element

        element_list = self.filter_elements(element_list)
        # After finding the labels and filtering for duplicates and hidden elements, we put them in the label_assignments dictionary with the value being the type of credentials we are filling
        # We also add their for attribute into the keyword list so that the generic_element_finder can find the input field to fill
        for web_element in element_list:
            self.label_assignments[web_element] = type_string
            id_value = web_element.get_attribute("for")
            if id_value is not None and id_value is not "":
                self.synonyms[type_string].append(id_value)

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
