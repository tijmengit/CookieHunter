from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

from selenium.webdriver.remote.webelement import WebElement
from tldextract import extract
from typing import Optional, Tuple, Dict, List, Union
import urllib.parse as urlparse
from DatabaseManager import DatabaseManager
from EmailVerifier import EmailVerifier
from Helper import *


class Browser:

    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser_options = Options()
        self.browser_options.add_experimental_option("prefs", selenium_prefs)
        self.browser = webdriver.Chrome(driver_path, options=self.browser_options)
        self.browser.set_page_load_timeout(10)
        self.db = DatabaseManager()
        self.emailVerifier = EmailVerifier()

        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url
        ext = extract(home_url)
        self.identifier = ext.domain + "1"
        self.db.add_new_webpage(self.identifier,
                                {'home_url': home_url, 'login_url': login_url, 'register_url': register_url})
        # Credentials
        self.fields = ["email", "password", "name", "username"]
        self.credentials = getCredentials(self.identifier)
        self.synonyms = getSynonyms()
        self.label_assignments = {}
        self.attribute_assignments = {}

    def register(self) -> bool:
        if not self.register_url:
            url = self.home_url
            self.browser.get(self.home_url)
        else:
            url = self.register_url
            self.browser.get(self.register_url)

        # Check and possibly remove cookie popup
        if self.__cookie_box_oracle():
            self.__cookie_accept(url)

        # Navigate to register url if necessary
        if not self.register_url:
            if self.__navigate_to_register():
                print('Registration url found')
            elif self.__identify_form() == 'register':
                print('Registration form on homepage')
            else:
                print('No registration url found')
                return False

        checks = self.browser.find_elements(By.XPATH, "//input[@type='checkbox']")
        for check in self.__filter_elements(checks):
            check.click()

        creds_for_register = self.__fill_attributes()

        # Comment this out to submit registration:
        if len(creds_for_register) > 0:
            # print("At least one input field has been filled")
            return self.__submit_registration(creds_for_register)
        else:
            # print("No submission done")
            return False

    def registration_oracle(self, creds_for_register: Dict[str, str]) -> bool:
        """
        3 checks for registration oracle:
        1. visit registration url and check if input fields are still there
        2. visit homepage and check for credentials passed to registration
        3. attempt to login
        """
        # 1. visit registration url and check for input fields used to register
        try:
            self.browser.get(self.register_url)
        except Exception as e:
            pass

        self.__fill_attributes()
        if self.__identify_form() == 'no form':
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

    def login(self) -> None:

        if not self.login_url:
            url = self.home_url
            self.browser.get(self.home_url)
        else:
            url = self.login_url
            self.browser.get(self.login_url)

        if self.__cookie_box_oracle():
            self.__cookie_accept(url)

        if not self.login_url:
            self.__navigate_to_login()

        creds_for_login = self.__fill_attributes()
        print("form filling complete")
        if len(creds_for_login) > 0:
            for web_element, field in self.attribute_assignments.items():
                try:
                    web_element.submit()
                    print(f'========== Login Form Submitted ==========')
                    break
                except Exception as e:
                    print(e)

    def login_oracle(self) -> bool:
        """
        Step 1: Refetch page and check whether submitted form is still there
        If False: We are logged in
        Else: (Follow)
        Step 2: Check if Account Identifiers are present + Logout Button
        If True: We are logged in
        Else: We are not logged in
        Step 3: Check false positves
        [send HTTP request without any cookies and consult login oracle once again]
        """
        logged_in = False
        second_step = False
        self.browser.get(self.login_url)

        for field in self.fields:
            elements = self.__generic_element_finder(f"//input[@type='{field}']", self.synonyms[field], field)
            if not elements:
                logged_in = True
            else:
                logged_in = False  # if one element is not empty --> go to step 2
                second_step = True
                break

        if second_step:
            self.browser.get(self.home_url)
            for value in self.credentials.values():
                if value in self.browser.page_source:
                    logged_in = True

        return logged_in

    def __login_oracle_help(self, website: str):
        self.browser.execute_script(f'''window.open("{website}","_blank");''')
        self.browser.switch_to.window(self.browser.window_handles[1])

    def __filter_elements(self, element_list: List[WebElement]) -> List[WebElement]:
        iterator = filter(lambda element: element.is_displayed(), set(element_list))
        return list(iterator)

    def __fill_attributes(self) -> Dict[str, str]:
        creds_filled = {}
        self.attribute_assignments = {}
        self.label_assignments = {}
        # label and input field searching done here
        for field in self.fields:
            self.__label_finder(self.synonyms[field], field)
            self.__generic_element_finder(f"//input[@type='{field}']", self.synonyms[field], field)

        # filling in the elements depending on their labels here, we iterate through labels and look for the input
        # fields to match with labels for attributes
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
                            creds_filled[field] = self.credentials[field]

        for web_element, field in self.attribute_assignments.items():
            if web_element.get_attribute("value") == "":
                web_element.send_keys(self.credentials[field])
                creds_filled[field] = self.credentials[field]

        return creds_filled

    def __submit_registration(self, creds_for_register: Dict[str, str]) -> bool:
        for web_element, field in self.attribute_assignments.items():
            try:
                sleep(1)
                web_element.submit()
                print(f'========== Registration Form submitted ==========')
                break
            except Exception as e:
                print(e)

        email_received = False
        msgId, links = self.__verifyEmail(max_tries=3)
        if msgId:
            print("Verification mail received")
            email_received = True
            for link in links:
                self.browser.get(link)
                sleep(3)

            self.db.update_web_page(self.identifier, {'verified': True})
            self.emailVerifier.messageRead(msgId)

        if email_received or self.registration_oracle(creds_for_register):
            print(f'registration successful, adding {self.home_url} to database')
            self.__fill_database(able_to_fill_register=True, able_to_fill_login=True, registered=True, captcha=False,
                                 creds_for_register=creds_for_register)
            return True
        else:
            return False

    def __verifyEmail(self, max_tries: int = 6) -> Tuple[Optional[str], list]:
        tries = 1
        while tries <= max_tries:
            delay = 2 ** tries
            sleep(delay)
            msgId, links = self.emailVerifier.getUnreadEmailLinks(self.identifier, max=30, days=30)
            if len(links) > 0:
                return msgId, links
            tries += 1
        return None, []

    def __fill_database(self, able_to_fill_register: bool, able_to_fill_login: bool,
                        registered: bool, captcha: bool, creds_for_register: Dict[str, str]) -> None:
        data = {'register_data': creds_for_register, 'able_to_fill_register': able_to_fill_register,
                'able_to_fill_login': able_to_fill_login, 'registered': registered, 'captcha': captcha}
        self.db.update_web_page(self.identifier, data)

    def __cookie_box_oracle(self) -> bool:
        """
        Function to check for a cookie box, which asks for consent
        :return: Cookie box present
        """
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

    def __cookie_accept(self, url: str) -> None:
        accept_button_options = self.__generic_buttons(self.synonyms['cookie-accept'])
        for b in accept_button_options:
            try:
                b.click()
                self.browser.get(url)
                return
            except Exception as e:
                pass

    def __navigate_to_register(self) -> bool:
        url = self.__get_sitemap(self.synonyms['register'])
        if len(url) > 0:
            self.register_url = url[0]
            self.browser.get(self.register_url)
            return True
        else:
            return False

    def __navigate_to_login(self) -> None:
        url = self.__get_sitemap(self.synonyms['login'])
        if len(url) > 0:
            self.login_url = url[0]
            self.browser.get(self.login_url)

    def __identify_form(self) -> str:
        pwd_fields = 0
        name_fields = 0
        input_fields = 0
        for web_element, field in self.attribute_assignments.items():
            if web_element.get_attribute("value") == "" or len(web_element.get_attribute("value")) > 1:
                input_fields += 1
                if field == 'password':
                    pwd_fields += 1
                elif field == 'name':
                    name_fields += 1
        if pwd_fields > 1:
            return 'register'
        if name_fields > 0:
            return 'register'
        if pwd_fields == 1:
            return 'login'
        if input_fields == 0:
            return 'no form'
        return 'unknown'

    def __get_sitemap(self, keywords: List[str]) -> List[str]:
        depth = 2
        limit = 50

        queue = [(self.home_url, 0)]
        found = []
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

                if page[1] < depth \
                        and clean_link not in handled \
                        and clean_link not in found \
                        and elem in self.synonyms['login']:
                    queue.append((clean_link, page[1] + 1))
                    queue = sorted(queue, key=lambda x: x[1])

        return found

    def __generic_element_finder(self, x_path_text: str, text_list: List[str], type_string: str) -> List[WebElement]:
        """
        Function that finds form elements that will be filled
        :param x_path_text: "//input[@type='{plc}']" finding inputs based on their types
        :param text_list: manually curated keyword list
        :param type_string: what type of credentials we are filling
        :return: None
        """
        element_list = []
        element = self.browser.find_elements(By.XPATH, x_path_text)
        element_list = element_list + element

        for text in text_list:
            if text not in self.browser.page_source:
                continue

            element = self.browser.find_elements(By.NAME, text)
            element_list = element_list + element

            element = self.browser.find_elements(By.TAG_NAME, text)
            element_list = element_list + element

            element = self.browser.find_elements(By.ID, text)
            element_list = element_list + element

            placeholder = f'//input[@placeholder="{text}"]'
            element = self.browser.find_elements(By.XPATH, placeholder)
            element_list = element_list + element

            placeholder = f'//input[@aria-label="{text}"]'
            element = self.browser.find_elements(By.XPATH, placeholder)
            element_list = element_list + element

        element_list = self.__filter_elements(element_list)
        # After finding the elements and filtering for duplicates and hidden elements, we put them in the
        # attribute_assignments dictionary with the value being the type of credentials we are filling
        for web_element in element_list:
            self.attribute_assignments[web_element] = type_string
        return element_list

    def __label_finder(self, text_list: List[str], type_string: str) -> None:
        """
        Function that finds label elements
        :param text_list: manually curated keyword list
        :param type_string: what type of credentials we are filling
        :return: None
        """
        element_list = []
        for text in text_list:
            element = self.browser.find_elements(By.XPATH, f"//label[contains(text(),'{text}')]")
            element_list = element_list + element
            inner_span = self.browser.find_elements(By.XPATH, f"//label/descendant::span[contains(text(),'{text}')]")
            for span_element in inner_span:
                element = span_element.find_elements(By.XPATH, "./..")
                element_list = element_list + element

        element_list = self.__filter_elements(element_list)
        # After finding the labels and filtering for duplicates and hidden elements, we put them in the
        # label_assignments dictionary with the value being the type of credentials we are filling We also add their
        # for attribute into the keyword list so that the generic_element_finder can find the input field to fill
        for web_element in element_list:
            self.label_assignments[web_element] = type_string
            id_value = web_element.get_attribute("for")
            if id_value is not None and id_value is not "":
                self.synonyms[type_string].append(id_value)

    def __generic_input_element_finder(self, text_list: List[str]) -> List[WebElement]:
        """
        This function returns generic input elements.
        !! This will not work for input values for "name" since it will also match username input type
        :param text_list:
        :return: input element
        """
        element_set = set()
        attr = ['@id', '@name', '@placeholder']
        for syn in text_list:
            for a in attr:
                if ' ' in syn:
                    continue
                elements = self.browser.find_elements_by_xpath(f'//input[contains({a}, {syn})]')
                for element in elements:
                    element_set.add(element)
        return self.__filter_elements(list(element_set))

    def __generic_buttons(self, text_list: List[str]) -> List[WebElement]:
        button_set = set()
        for syn in text_list:
            x_paths = ['//button[text()="' + syn + '"]']
            for path in x_paths:
                buttons = self.browser.find_elements_by_xpath(path)
                for b in buttons:
                    button_set.add(b)
        return self.__filter_elements(list(button_set))

    def get_cookies(self) -> Dict[str, str]:
        return self.browser.get_cookies()

    def add_cookie(self, cookie: Dict[str, str]) -> None:
        self.browser.add_cookie(cookie)

    def delete_cookies(self, cookies: Optional[List[Union[str, Dict[str, str]]]] = None) -> None:
        if cookies is None:
            cookies = []
        if not cookies:
            self.browser.delete_all_cookies()
        else:
            for cookie in cookies:
                self.delete_cookie(cookie)

    def delete_cookie(self, cookie: Union[str, Dict[str, str]]) -> None:
        if type(cookie) is dict:
            cookie = cookie['name']
        self.browser.delete_cookie(cookie)

    def refresh(self) -> None:
        self.browser.refresh()

    def close(self) -> None:
        self.browser.quit()
