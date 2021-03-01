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
        cookie_list_unfiltered = self.browser.get_cookies()
        cookie_list = [c for c in cookie_list_unfiltered if not c['secure'] or not c['httpOnly']]
        # Initialization from bottom and top, starting with full set and with single cookies
        # There will be 2 skipping sets which will be compared with to check if a set still has to be evaluated or not
        # e.g. if Cookie A is sufficient enough to login, every other set including A can be skipped: A -> skip_enabling_set
        # e.g. if we have 4 Cookies A,B,C,D and A,B,C is not sufficient enough to login implies that we need D to login
        # --> D will be put in skip_disabling_set and if a set does not contain at least 1 elem in that set can be skipped as well
        cookie_set = [i for i in range(0,len(cookie_list))]
        bot_set = [[]]
        top_set = [cookie_set[:]]

        b_filter = []
        t_filter = []

        end_result = set()

        level = 0
        total_counter =0

        while level < len(cookie_set):
            if level % 2 == 0:
                bot_set_copy = bot_set[:]
                bot_set = []
                duplicate_array = []        # arrays tested at this level
                for array in bot_set_copy:
                    for elem in cookie_set:
                        tmp = array[:]
                        skip_b = False
                        skip_t = True
                        if elem not in tmp:
                            tmp.append(elem)
                            tmp.sort()
                            #print("try: ",tmp)
                            if tmp not in duplicate_array: #check if not only permutation
                                duplicate_array.append(tmp)
                                for f in b_filter:          # check if combination can be skipped because subset is already sufficient
                                    if set(tuple(f)).issubset(tuple(tmp)):
                                        skip_b = True
                                        break
                                if not t_filter:
                                    skip_t = False
                                for f in t_filter:          # check if combination can be skipped because subset is already sufficient
                                    if tuple([f]) in tuple(tmp):
                                        skip_t = False
                                        break
                                if not skip_b and not skip_t:
                                    total_counter += 1
                                    cookies = [cookie_list[i] for i in tmp]
                                    if self.check_cookie_set(cookies):
                                        end_result.add(tuple(tmp))
                                        b_filter.append(tmp)
                                    else:
                                        if tmp not in bot_set:
                                            bot_set.append(tmp)
            else:
                top_set_copy = top_set[:]
                top_set = []
                t_filter_copy = t_filter[:]
                for array in top_set_copy:
                    for elem in cookie_set:
                        tmp = array[:]
                        skip_b = False
                        skip_t = True
                        if elem in tmp:
                            tmp.remove(elem)
                            tmp.sort()
                            removed_elem = elem
                            for f in b_filter:          # check if combination can be skipped because subset is already sufficient
                                if set(tuple(f)).issubset(tuple(tmp)):
                                    skip_b = True
                                    break
                            if not t_filter_copy:
                                skip_t = False
                            for f in t_filter_copy:          # check if combination can be skipped because subset is already sufficient
                                if tuple([f]) in tuple(tmp):
                                    skip_t = False
                                    break
                            if tmp not in top_set:
                                top_set.append(tmp)
                            if not skip_b and not skip_t:
                                total_counter += 1
                                cookies = [cookie_list[i] for i in tmp]
                                if self.check_cookie_set(cookies):
                                    end_result.add(tuple(tmp))
                                elif removed_elem not in t_filter:
                                    t_filter.append(removed_elem)
            level += 1
        return([( [cookie_list[elem] for elem in comb]) for comb in end_result])

    def check_cookie_set(self, cookie_set=[]):
        self.browser.delete_cookies()
        for cookie in cookie_set:
            self.browser.add_cookie(cookie)
        self.browser.refresh()
        return self.browser.login_oracle()

    def __evaluate_cookies(self, cookie_set):
        self.browser.delete_cookies(cookie_set)
        self.browser.refresh()
        return self.browser.login_oracle()
