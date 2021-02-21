from selenium import webdriver
import os
import platform

class CookieAuditor:
    def __init__(self, driver_path, base_url, cookies):
        self.driver_path = driver_path
        self.base_url = base_url
        self.cookies = cookies


    def findVulnerableCookies(self, cookies):
        critical_cookies = {'secure': [], 'httpOnly': []}
        for cookie in cookies:
            for attr in critical_cookies:
                if(cookie[attr]):
                    critical_cookies[attr].append(cookie)
        print(critical_cookies)


if __name__ == "__main__":
    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    base_url = "https://www.mentimeter.com"
    stolen_cookies = {}
    browser = webdriver.Chrome(PATH)
    browser.get(base_url)
    cookies = browser.get_cookies()

    auditor = CookieAuditor(PATH, base_url, cookies)
    auditor.findVulnerableCookies(cookies)
