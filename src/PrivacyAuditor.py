import platform
import os
from typing import List, Dict, Set
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup as BS
import urllib.parse as urlparse
import multiprocessing as MP
import re
import hashlib
import base64




class PrivacyAuditor:
    keywords = ['user', 'profile', 'account', 'settings', 'cart', 'shoppingcart', 'shop', 'preferences']
    ignore = ['logout', 'login', 'register', 'sign-up', 'sign-in', 'sign-out', 'stories', 'blog', 'forum', 'campaigns',
              'book', 'books', 'genres', 'product', 'products', 'news', 'stories', 'story', 'choiceawards',
              'list', 'reviews', 'review', 'quotes', 'quote', 'releases', 'films', 'movies', 'film', 'movie']

    def __init__(self, driver_path: str, browser_options: List[str]) -> None:
        self.driver_path = driver_path
        self.browser_options = Options()
        self.base_url = None
        self.cookies = None
        self.information = None
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

    def audit(self, base_url: str, cookies: List[Dict[str, str]], information: Dict[str, str]) -> Dict[str, List[str]]:
        self.base_url = base_url
        self.cookies = cookies
        self.information = self.augment_reference_information(information)

        print('########### PRIVACY AUDITOR ###########')
        print('======= Interesting Pages ======')
        pages = self.get_interesting_pages()
        print(pages, '\n')

        browser = self.create_browser(True)

        print('========== Page Leaks ==========')
        page_leaks = self.find_page_leaks(browser, pages)
        print(page_leaks, '\n')

        print('========= Cookie Leaks =========')
        cookie_leaks = self.inspect_cookies(browser)
        print(cookie_leaks, '\n')

        print('========== URL Leaks ===========')
        url_leaks = self.inspect_urls(pages)
        print(url_leaks, '\n')

        print('========= Storage Leaks ========')
        storage_leaks = self.inspect_storage(browser)
        print(storage_leaks, '\n')

        browser.quit()

        return {
            'page_leaks': list(page_leaks),
            'cookie_leaks': list(cookie_leaks),
            'url_leaks': list(url_leaks),
            'storage_leaks': list(storage_leaks),
        }

    def inspect_urls(self, urls: List[str]) -> Set[str]:
        leaks = set()
        for url in urls:
            decoded = self.base64_finder(url)

            for info_type, info in self.information.items():
                page_url = urlparse.unquote(url)
                page_url_tmp = re.sub('[^A-Za-z]+', '', page_url).lower()
                info_tmp = re.sub('[^A-Za-z]+', '', info).lower()

                if info_tmp in page_url_tmp:
                    leaks.add(info_type)
                    continue

                for d in decoded:
                    if info in d:
                        leaks.add(info_type)
                        break

        return leaks

    def inspect_storage(self, browser: WebDriver) -> Set[str]:
        leaks = set()

        local = browser.execute_script('return {...window.localStorage}')
        session = browser.execute_script('return {...window.sessionStorage}')

        decoded = []
        for name, value in local.items():
            decoded.extend(self.base64_finder(name))
            decoded.extend(self.base64_finder(value))
        for name, value in session.items():
            decoded.extend(self.base64_finder(name))
            decoded.extend(self.base64_finder(value))

        for info_type, info in self.information.items():
            for d in decoded:
                if info in d:
                    leaks.add(info_type)
                    break

            for name, value in local.items():
                if info == name or info == value:
                    leaks.add(info_type)
                    break

            for name, value in session.items():
                if info == name or info == value:
                    leaks.add(info_type)
                    break

        return leaks

    def inspect_cookies(self, browser: WebDriver) -> Set[str]:
        leaks = set()
        cookies = browser.get_cookies()

        decoded = []
        for cookie in cookies:
            decoded.extend(self.base64_finder(cookie['name']))
            decoded.extend(self.base64_finder(cookie['value']))

        for info_type, info in self.information.items():
            for d in decoded:
                if info in d:
                    leaks.add(info_type)
                    break

            for cookie in cookies:
                if info in cookie['name'] or info in cookie['value']:
                    leaks.add(info_type)
                    break
        return leaks

    def find_page_leaks(self, browser: WebDriver, pages: List[str]) -> Set[str]:
        leaks = set()
        for page in pages:
            browser.get(page)

            decoded = self.base64_finder(browser.page_source)

            for info_type, info in self.information.items():
                elements = browser.find_elements_by_xpath(f'//*[text()="{info}" or @value="{info}"]')
                if elements:
                    leaks.add(info_type)
                    continue

                for d in decoded:
                    if info in d:
                        leaks.add(info_type)
                        break

        return leaks

    def get_interesting_pages(self) -> Set[str]:
        manager = MP.Manager()
        without_cookies = manager.list()
        with_cookies = manager.list()
        p1 = MP.Process(target=self.get_sitemap, args=(False, without_cookies))
        p2 = MP.Process(target=self.get_sitemap, args=(True, with_cookies))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        without_cookies = without_cookies[:]
        with_cookies = with_cookies[:]
        return set(with_cookies) - set(without_cookies)

    def get_sitemap(self, use_cookies: bool, return_value: List) -> List[str]:
        depth = 2
        limit = 50
        browser = self.create_browser(use_cookies)

        queue = [(self.base_url, 0)]
        found = [self.base_url]

        base = urlparse.urlparse(self.base_url).netloc

        while queue:
            page = queue.pop(0)
            browser.get(page[0])
            soup = BS(browser.page_source, 'html.parser')

            for link in soup.select('body a')[:limit]:
                full_link = urlparse.urljoin(self.base_url, link.get('href'))
                parsed_link = urlparse.urlparse(full_link)
                path = parsed_link.path.split('/')
                elem = path[1] if len(path) >= 2 else ''
                # create clean link without queries, parameters or fragments
                clean_link = f'{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}'

                if parsed_link.netloc == base \
                        and elem in self.keywords \
                        and clean_link not in found:
                    found.append(clean_link)

                    if page[1] < depth:
                        queue.append((clean_link, page[1] + 1))
                        queue = sorted(queue, key=lambda x: x[1])

        browser.quit()
        return_value.extend(found)

    def create_browser(self, use_cookies: bool) -> WebDriver:
        browser = webdriver.Chrome(self.driver_path, options=self.browser_options)
        browser.get(self.base_url)
        if use_cookies:
            for cookie in self.cookies:
                browser.delete_cookie(cookie['name'])
                browser.add_cookie(cookie)
            browser.refresh()
        return browser

    def augment_reference_information(self, information: Dict[str, str]) -> Dict[str, str]:
        augmented = {}
        hashes = ['md5', 'sha1', 'sha256', 'sha512']
        for key, value in information.items():
            augmented[key] = value
            for hash in hashes:
                augmented[f'{key}_{hash}'] = getattr(hashlib, hash)(str.encode(value)).hexdigest()

        return augmented

    def base64_finder(self, content: str) -> List[str]:
        pattern = r'(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=|[A-Za-z0-9+\/]{4})'
        matches = list(set(re.findall(pattern, content)))
        decoded = list(filter(None, [self.base64_decoder(match) for match in matches]))
        return decoded

    def base64_decoder(self, content: str) -> str:
        decoded = base64.b64decode(content)
        try:
            utf8 = str(decoded, 'utf-8')
            return utf8
        except UnicodeDecodeError:
            return ''


if __name__ == '__main__':
    PATH = os.getenv(
        'LOCALAPPDATA') + '/ChromeDriver/chromedriver' if platform.system() == 'Windows' else '/usr/local/sbin/chromedriver'
    audit_url = 'https://www.goodreads.com/'
    stolen_cookies = [
        {'name': '_session_id2', 'value': '1faac5fd1782ccdf1def9419bde66406', 'domain': 'www.goodreads.com'},
        {'name': 'locale', 'value': 'en', 'domain': 'www.goodreads.com'},
        {'name': 'logged_out_browsing_page_count', 'value': '2', 'domain': 'www.goodreads.com'},
        {'name': 'cssid', 'value': '848-2350035-9701439', 'domain': 'www.goodreads.com'},
        {'name': 'test1', 'value': 'cookiehunterproject', 'domain': 'www.goodreads.com'},
        {'name': 'test2', 'value': 'YXNkZmFzZGZhc2RmY29va2llaHVudGVycHJvamVjdEBnbWFpbC5jb21hc2RmYXNkZmFzZGY=', 'domain': 'www.goodreads.com'},
        {'name': 'test3', 'value': 'd5c2fba5e06e4ef718282cc6331ce158', 'domain': 'www.goodreads.com'},
        {'name': 'test4', 'value': 'Jan Janssen', 'domain': 'www.goodreads.com'},

    ]

    reference_information = {
        'firstname': 'Jan',
        'lastname': 'Janssen',
        'fullname': 'Jan Janssen',
        'city': 'Vijfhuizen',
        'country': 'Netherlands',
        'password': 'passwordRandom123!',
        'email': 'cookiehunterproject@gmail.com',
        'username': 'CookieHunter007',
    }

    options = ['--headless']
    options = []

    auditor = PrivacyAuditor(PATH, options)
    leaks = auditor.audit(audit_url, stolen_cookies, reference_information)
    print('========= Found leaks ==========')
    print(leaks)
