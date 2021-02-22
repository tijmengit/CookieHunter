import platform
import os
from typing import List, Dict
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as BS
import urllib.parse as urlparse
from pprint import pprint


class PrivacyAuditor:
    keywords = []
    ignore = ['logout', 'login', 'register', 'stories', 'blog', 'forum', 'campaigns']

    def __init__(self, driver_path: str, base_url: str, cookies: List[Dict[str, str]], auth: bool,
                 browser_options: List[str]):
        self.driver_path = driver_path
        self.base_url = base_url
        self.cookies = cookies
        self.auth = auth
        self.browser_options = Options()
        for option in browser_options:
            self.browser_options.add_argument(option)

    def audit(self):
        depth = 1
        without_cookies = self.get_sitemap(False, depth)
        with_cookies = self.get_sitemap(True, depth)
        pprint(set(with_cookies) - set(without_cookies))

    def get_sitemap(self, use_cookies: bool, depth: int):
        pprint(f'Fetching sitemap for {self.base_url} with{"out" if not use_cookies else ""} cookies...')
        browser = webdriver.Chrome(self.driver_path, options=self.browser_options)
        base = urlparse.urlparse(self.base_url).netloc

        if use_cookies:
            browser.get(self.base_url)
            for cookie in self.cookies:
                browser.delete_cookie(cookie['name'])
                browser.add_cookie(cookie)
            browser.refresh()

        queue = [(self.base_url, 0)]
        found = [self.base_url]

        # TODO fix to ignore pages like productlists (e.g. "https://something.com/products/<id:0-9999999999>")

        while queue:
            url = queue.pop(0)
            browser.get(url[0])
            soup = BS(browser.page_source, 'html.parser')
            for link in soup.find_all('a'):
                l = urlparse.urljoin(self.base_url, link.get('href'))
                parsed = urlparse.urlparse(l)
                path = parsed.path.split('/')
                elem = path[1] if len(path) >= 2 else ''
                if parsed.netloc == base \
                        and elem not in self.ignore \
                        and url[1] < depth \
                        and l not in found:
                    found.append(l)
                    queue.append((l, url[1] + 1))
                    queue = sorted(queue, key=lambda x: x[1])

        browser.quit()
        return found


if __name__ == '__main__':
    PATH = os.getenv(
        'LOCALAPPDATA') + '/ChromeDriver/chromedriver' if platform.system() == 'Windows' else '/usr/local/sbin/chromedriver'
    url = 'https://www.goodreads.com/'
    stolen_cookies = [
        {'name': '_session_id2', 'value': 'dad38f1f6290312d962baae42e7e3aec', 'domain': 'www.goodreads.com'},
        {'name': 'locale', 'value': 'en', 'domain': 'www.goodreads.com'},
        {'name': 'logged_out_browsing_page_count', 'value': '2', 'domain': 'www.goodreads.com'},
        {'name': 'cssid', 'value': '848-2350035-9701439', 'domain': 'www.goodreads.com'},
    ]

    options = ['--headless']
    options = []

    auth = True
    auth = False

    auditor = PrivacyAuditor(PATH, url, stolen_cookies, auth, options)
    auditor.audit()
