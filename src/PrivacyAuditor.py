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
    ignore = ['stories', 'blog', 'forum', 'campaigns']

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
        depth = 2
        without_cookies = self.get_sitemap(False, depth)
        # with_cookies = self.get_sitemap(True, depth)
        pprint(without_cookies)

    def get_sitemap(self, use_cookies: bool, depth: int):
        browser = webdriver.Chrome(self.driver_path, options=self.browser_options)
        base = urlparse.urlparse(self.base_url).netloc

        if use_cookies:
            # TODO implement cookies
            pass

        queue = [(self.base_url, 0)]
        found = [self.base_url]

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

        return found


if __name__ == '__main__':
    PATH = os.getenv(
        'LOCALAPPDATA') + '/ChromeDriver/chromedriver' if platform.system() == 'Windows' else '/usr/local/sbin/chromedriver'
    url = 'https://www.mentimeter.com/'
    stolen_cookies = [
        {'name': '__cfduid', 'value': 'd8d0380127035d527efb231fa6e483cee1613910986'},
        {'name': 'data-split-country', 'value': 'NL'},
        {'name': 'intercom-session-g5fg6k76',
         'value': 'NFZQWWlsd2NkYnF5UUV4TUNqdnVoSTlRaDBCMVJZWjlabjJ6bld6TnlnWVluUWhCdndkUCt5cDFBSlRWbGNCdC0tVjFPUjRqYjFYa2tKaDVEcG96Q1R1QT09--d4b9b4e8806237342f49fda839d8fd8e99f03645'},
        {'name': 'intercom-id-g5fg6k76', 'value': '34818d21-8bec-4409-a0f5-d168fa0ea11b'},
        {'name': 'visitor_token',
         'value': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aXNpdG9yS2V5IjoiMTg4NjUxODAtZTZjMi00MzNiLWE1NzEtYjg1MjZhYzMyNjUzIiwiaWF0IjoxNjEzOTEwOTg2fQ.kjd_svnGsaq6ai5_1EtBAoy7lMcavtnCmLfKMYBmNcM'},
        {'name': '_dd_s', 'value': 'rum=0&expire=1613911966371'},
    ]

    auditor = PrivacyAuditor(PATH, url, stolen_cookies, True, ['--headless'])
    auditor.audit()
