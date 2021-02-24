from selenium import webdriver
import os
import platform


class CookieAuditor:
    def __init__(self, browser):
        self.browser = browser

    def findVulnerableCookies(self):
        critical_cookies = {'secure': [], 'httpOnly': []}
        vulnerable = {'secure': None, 'httpOnly': None}
        if not self.browser.login_oracle():
            self.browser.login()

        for cookie in self.browser.get_cookies():
            for attr in critical_cookies:
                if (cookie[attr]):
                    critical_cookies[attr].append(cookie)
        tested = []
        for attr in critical_cookies:
            if not critical_cookies[attr]:
                vulnerable[attr] = True
            else:
                # Check if httpOnly set is same or subset of secure set.
                # If the same then vulnarability status of httponly and secure are the same.
                # If httpOnly is a subset of secure and secure is vulnerable,
                # then httpOnly is also vulnerable as we would send more cookies then in the secure excluded test
                for tested_attr in tested:
                    tested_set = critical_cookies[tested_attr]
                    setDiff = [i for i in critical_cookies[attr] if i not in tested_set]
                    if not setDiff and len(critical_cookies[attr]) == len(tested_set):
                        vulnerable[attr] = vulnerable[tested_attr]
                    else:
                        if vulnerable[tested_attr] and len(critical_cookies[attr]) < len(tested_set):
                            vulnerable[attr] = True

                # Evaluate if login still succeeds if we remove one set of critical cookies (secure or httpOnly)
                # If login is successful we know that these cookies are vulnerable.
                if vulnerable[attr] is None:
                    vulnerable[attr] = self.__evaluate_cookies(critical_cookies[attr])

            tested.append(attr)
            if not vulnerable[attr]:
                self.browser.login()

        return vulnerable

    def findAuthCookies(self):
        # Retrieve Cookies
        cookie_list = self.browser.get_cookies()

        # Initialization from bottom and top, starting with full set and with single cookies
        # There will be 2 skipping sets which will be compared with to check if a set still has to be evaluated or not
        # e.g. if Cookie A is sufficient enough to login, every other set including A can be skipped: A -> skip_enabling_set
        # e.g. if we have 4 Cookies A,B,C,D and A,B,C is not sufficient enough to login implies that we need D to login
        # --> D will be put in skip_disabling_set and if a set does not contain at least 1 elem in that set can be skipped as well
        poset_bottom = cookie_list.copy()
        poset_top = [cookie_list.copy()]
        skip_enabling_set = []
        skip_disabling_set = []

        # This would be the first round - will make it recursive
        for i in poset_bottom:
            print(i)
            print(self.__evaluate_cookies(i))
        for j in poset_top:
            print(j)
            print(self.__evaluate_cookies(j))


    def __evaluate_cookies(self, cookie_set):
        self.browser.delete_cookies(cookie_set)
        self.browser.refresh()
        return self.browser.login_oracle()
