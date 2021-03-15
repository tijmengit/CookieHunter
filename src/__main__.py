
import sys
import traceback
from CookieHunter.src.Browser import *
from CookieHunter.src.CookieAuditor import *

if __name__ == "__main__":
    home_url = "https://www.goodreads.com"
    login_url = "https://www.goodreads.com/user/sign_in"
    register_url = "https://www.goodreads.com/user/sign_up"
    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    browser = Browser(home_url=home_url, login_url=login_url, register_url=register_url, driver_path=PATH)

    try:
        browser.register()
        # browser.login()
        # c_auditor = CookieAuditor(browser)
        #vulnerable = c_auditor.findVulnerableCookies()
        #print(vulnerable)
        # auth_cookies = c_auditor.findAuthCookies()
        # print(auth_cookies)
        browser.close()
    except:
        traceback.print_exc()
        browser.close()


    # with open('../data/sites.json') as sites_file:
    #     sites = json.load(sites_file)
    #     for site in sites:
    #         browser = Browser(home_url=site['home_url'], login_url=site['login_url'], register_url=site['register_url'], driver_path=PATH)
    #         browser.register()
