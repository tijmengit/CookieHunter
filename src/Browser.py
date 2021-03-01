from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec



class Browser:

    def __init__(self, home_url, login_url, register_url, driver_path):
        self.browser = webdriver.Chrome(driver_path)
        self.home_url = home_url
        self.login_url = login_url
        self.register_url = register_url

        # Credentials
        self.email_address = "cookiehunterproject@gmail.com"
        self.pwd = "passwordRandom123!"
        self.name = "Janssen "
        self.username = "CookieHunter007"
        self.email_synonyms = ['user_email', 'email', 'e_mail', 'useremail', 'userEmail', 'mail', 'uemail',
                               'User_email', 'Email', 'E_mail', 'Useremail', 'UserEmail', 'Mail', 'Uemail',
                               'User_email_address', 'Email_address', 'email_address', 'emailadress',
                               'UserEmailAddress', 'Email address', 'Email Address', 'EMAIL',
                               'MailAdress'
                               ]
        self.password_synonyms = ['user_password', 'password', 'pword', 'userpassword', 'userpwd', 'pwd', 'PWD',
                                  'u_password', 'passw', 'p_word', 'UserPassword', 'UserPwd', 'Pwd', 'pass', 'Password',
                                  'User Password'
                                  ]
        self.name_synonyms = ['name_first', 'name', 'first_name', 'firstname', 'First_Name', 'f_name', 'firstName',
                              'User_efirstname', 'First_name', 'first_Name', 'NAME', 'F_NAME', 'FName',
                              'fname_', '_firstname', 'fullname', 'full_name', 'user_first_name', 'First Name', 'first name',
                              'nc_firstname', 'nc_firstname_required',

                              'last_name', 'lastname', 'last_Name', 'l_name', 'lastName',
                              'User_elastname', 'last_name', 'Last_Name', 'l_NAME', 'lName',
                              'lname_', '_lastname', 'user_last_name', 'Last Name', 'Last name', 'last name',
                              'nc_lastname', 'nc_lastname_required'

                              ]
        self.username_synonyms = ['username', 'uname', 'user_id', 'user_name', 'uName', 'u_Name', 'UserName',
                                  'user_name_new', 'new_username', 'user_username', 'user_username', 'user[username]', 'Username', 'nc_username', 'nc_username_required'
                                  ]
    def filter_elements(self, element_list):
        iterator = filter(lambda element: element.is_displayed(), set(element_list))
        return list(iterator)

    def register(self):
        self.browser.get((self.register_url))
        self.cookie_accept()
        # login_form = self.browser.find_element_by_xpath("//form[1]")
        checks = self.browser.find_elements(By.XPATH, "//input[@type='checkbox']")
        for check in checks:
            check.click()

        email = self.generic_element_finder("//input[@type='email']", self.email_synonyms)
        for field in email:
            field.send_keys(self.email_address)

        pwd = self.generic_element_finder("//input[@type='password']", self.password_synonyms)
        for field in pwd:
            field.send_keys(self.pwd)

        username = self.generic_element_finder("//input[@type='username']", self.username_synonyms)
        for field in username:
            field.send_keys(self.username)

        name = self.generic_element_finder("//input[@type='name']", self.name_synonyms)
        for field in name :
            field.send_keys(self.name)

        # button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
        # button.click()
        print("form filling complete")
        # name.submit()
        # button = browser.findElement(By.xpath("//button[text()='Sign up']")).click();
        # button.click()

    def cookie_accept(self):
        cookie_elements = ['cookieContainer', 'cookieOverlay', 'cookieAcceptForm']
        # text which could be inside cookie accept buttons:
        cookie_accept_elements = [ 'bevestig', 'Bevestig', 'confirm', 'Confirm','Accepteer',
                                  'accepteer',  'Accept','accept', 'cookies', 'Cookies', 'keuze', 'choice']
        cookie_present = False
        for el in cookie_elements:
            try:
                self.browser.find_element_by_xpath(f"//*[contains(text(), {el})]")
                cookie_present = True
                break
            except Exception as e:
                print(e)
        if cookie_present:
            for el in cookie_accept_elements:
                try:
                    accept_button_options = self.browser.find_elements_by_xpath(f"//button[contains(text(), {el})]")
                    for b in accept_button_options:
                        try:
                            b.click()
                            return
                        except Exception as e:
                            pass
                except Exception as e:
                    pass
        return

    def login(self):
        self.browser.get((self.login_url))
        email = self.generic_element_finder("//input[@type='email']", self.email_synonyms)
        for field in email:
            field.send_keys(self.email_address)

        pwd = self.generic_element_finder("//input[@type='password']", self.password_synonyms)
        for field in pwd:
            field.send_keys(self.pwd)

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
