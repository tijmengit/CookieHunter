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
    ignore = ['logout', 'login', 'register', 'sign-in', 'sign-out', 'stories', 'blog', 'forum', 'campaigns',
              'book', 'books', 'genres', 'product', 'products', 'news', 'stories', 'story', 'choiceawards',
              'list', 'reviews', 'review', 'quotes', 'quote', 'releases', 'films', 'movies', 'film', 'movie']

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
        pages = self.get_interesting_pages()

    def get_interesting_pages(self):
        depth = 1
        manager = MP.Manager()
        without_cookies = manager.list()
        with_cookies = manager.list()
        p1 = MP.Process(target=self.get_sitemap, args=(False, depth, without_cookies))
        p2 = MP.Process(target=self.get_sitemap, args=(True, depth, with_cookies))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        without_cookies = without_cookies[:]
        with_cookies = with_cookies[:]
        return set(with_cookies) - set(without_cookies)

    def get_sitemap(self, use_cookies: bool, depth: int, return_value: List):
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
            page = queue.pop(0)
            browser.get(page[0])
            soup = BS(browser.page_source, 'html.parser')
            for link in soup.find_all('a'):
                full_link = urlparse.urljoin(self.base_url, link.get('href'))
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


if __name__ == '__main__':
    PATH = os.getenv(
        'LOCALAPPDATA') + '/ChromeDriver/chromedriver' if platform.system() == 'Windows' else '/usr/local/sbin/chromedriver'
    url = 'https://www.goodreads.com/'
    stolen_cookies = [
        {'name': '_session_id2', 'value': 'ea8c83a1a1893ab157dbf0069ada1e52', 'domain': 'www.goodreads.com'},
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
