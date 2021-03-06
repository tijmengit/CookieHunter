import platform
import os
from typing import List, Dict
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as BS
import urllib.parse as urlparse
from pprint import pprint
import multiprocessing as MP


class PrivacyAuditor:
    keywords = []
    ignore = ['logout', 'login', 'register', 'sign-up', 'sign-in', 'sign-out', 'stories', 'blog', 'forum', 'campaigns',
              'book', 'books', 'genres', 'product', 'products', 'news', 'stories', 'story', 'choiceawards',
              'list', 'reviews', 'review', 'quotes', 'quote', 'releases', 'films', 'movies', 'film', 'movie']

    def __init__(self, driver_path: str, auth: bool, browser_options: List[str]):
        self.driver_path = driver_path
        self.auth = auth
        self.browser_options = Options()
        for option in browser_options:
            self.browser_options.add_argument(option)
        self.prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2
        }
        self.browser_options.add_experimental_option("prefs", self.prefs)

    def audit(self, base_url: str, cookies: List[Dict[str, str]], information: Dict[str, str]):
        page_leaks = self.find_page_leaks(base_url, cookies, information)

    def find_page_leaks(self, base_url: str, cookies: List[Dict[str, str]], information: Dict[str, str]):
        pages = self.get_interesting_pages(base_url, cookies)
        browser = self.create_browser(base_url, cookies)
        for page in pages:
            browser.get(page)
            for type, info in information.items():
                elements = browser.find_elements_by_xpath(f'//*[text()="{info}"]')
                if elements:
                    for element in elements:
                        print(page)
                        print(element.text)
                        print('=================')

    def get_interesting_pages(self, base_url: str, cookies: List[Dict[str, str]]):
        depth = 1
        manager = MP.Manager()
        without_cookies = manager.list()
        with_cookies = manager.list()
        p1 = MP.Process(target=self.get_sitemap, args=(base_url, None, depth, without_cookies))
        p2 = MP.Process(target=self.get_sitemap, args=(base_url, cookies, depth, with_cookies))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        without_cookies = without_cookies[:]
        with_cookies = with_cookies[:]
        return set(with_cookies) - set(without_cookies)

    def get_sitemap(self, base_url: str, cookies: List[Dict[str, str]], depth: int, return_value: List):
        browser = self.create_browser(base_url, cookies)

        queue = [(base_url, 0)]
        found = [base_url]

        base = urlparse.urlparse(base_url).netloc

        while queue:
            page = queue.pop(0)
            browser.get(page[0])
            soup = BS(browser.page_source, 'html.parser')
            for link in soup.find_all('a'):
                full_link = urlparse.urljoin(base_url, link.get('href'))
                parsed_link = urlparse.urlparse(full_link)
                path = parsed_link.path.split('/')
                elem = path[1] if len(path) >= 2 else ''
                if parsed_link.netloc == base \
                        and elem not in self.ignore \
                        and page[1] < depth \
                        and full_link not in found:
                    found.append(full_link)
                    queue.append((full_link, page[1] + 1))
                    queue = sorted(queue, key=lambda x: x[1])

        browser.quit()
        return_value.extend(found)

    def create_browser(self, base_url: str, cookies: List[Dict[str, str]]):
        browser = webdriver.Chrome(self.driver_path, options=self.browser_options)
        browser.get(base_url)
        if cookies:
            for cookie in cookies:
                browser.delete_cookie(cookie['name'])
                browser.add_cookie(cookie)
            browser.refresh()
        return browser


if __name__ == '__main__':
    PATH = os.getenv(
        'LOCALAPPDATA') + '/ChromeDriver/chromedriver' if platform.system() == 'Windows' else '/usr/local/sbin/chromedriver'
    url = 'https://www.goodreads.com/'
    stolen_cookies = [
        {'name': '_session_id2', 'value': '7d73483c9393ddb796006f6c6669e3bf', 'domain': 'www.goodreads.com'},
        {'name': 'locale', 'value': 'en', 'domain': 'www.goodreads.com'},
        {'name': 'logged_out_browsing_page_count', 'value': '2', 'domain': 'www.goodreads.com'},
        {'name': 'cssid', 'value': '848-2350035-9701439', 'domain': 'www.goodreads.com'},
    ]

    reference_information = {
        'firstname': 'Jan',
        'lastname': 'Janssen',
        'city': 'Vijfhuizen',
        'country': 'Netherlands',
        'password': 'passwordRandom123!',
        'email': 'cookiehunterproject@gmail.com',
        'username': 'CookieHunter007',
    }

    options = ['--headless']
    options = []

    auth = True
    auth = False
    # TODO move auth to .audit()
    auditor = PrivacyAuditor(PATH, auth, options)
    auditor.audit(url, stolen_cookies, reference_information)
