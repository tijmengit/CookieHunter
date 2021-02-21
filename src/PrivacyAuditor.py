import platform
import os
from selenium import webdriver


class PrivacyAuditor:
    def __init__(self, driver_path, base_url, cookies, auth):
        self.driver_path = driver_path
        self.base_url = base_url
        self.cookies = cookies
        self.auth = auth

    def audit(self):
        clean = self.get_sitemap(False, 3)

    def get_sitemap(self, use_cookies, depth):
        browser = webdriver.Chrome(self.driver_path)
        if use_cookies:
            browser.add_cookie(self.cookies)
        browser.get(self.base_url)
        return {}


if __name__ == '__main__':
    PATH = os.getenv("LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    base_url = "https://www.mentimeter.com"
    stolen_cookies = {}

    auditor = PrivacyAuditor(PATH, base_url, stolen_cookies, True)
    auditor.audit()
