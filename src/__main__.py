
import sys
import traceback
from Browser import *
from CookieAuditor import *
from PrivacyAuditor import *

def fullFlow():
    home_url = "https://www.goodreads.com"
    login_url = "https://www.goodreads.com/user/sign_in"
    register_url = "https://www.goodreads.com/user/sign_up"
    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    browser = Browser(home_url=home_url, login_url=login_url, register_url=register_url, driver_path=PATH)

    try:

        if True:
            browser.login()
            if browser.login_oracle():
                cookieAudit = CookieAuditor(browser)
                vulnerable = cookieAudit.findVulnerableCookies()
                if vulnerable['secure'] or vulnerable['httpOnly']:
                    vulnerableCookies = cookieAudit.findAuthCookies()

                    if vulnerableCookies:
                        options = ['--headless']
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
                        privacyAuditor = PrivacyAuditor(PATH, options)
                        leaks = privacyAuditor.audit(home_url, vulnerableCookies[0], reference_information)
                        print('========= Found leaks ==========')
                        print(leaks)
                        browser.db.update_web_page(browser.identifier, {"leaks": leaks})



    except:
        traceback.print_exc()
        browser.close()


if __name__ == "__main__":
    fullFlow()

    # try:
    #     browser.register()
    #     # browser.login()
    #     # c_auditor = CookieAuditor(browser)
    #     #vulnerable = c_auditor.findVulnerableCookies()
    #     #print(vulnerable)
    #     # auth_cookies = c_auditor.findAuthCookies()
    #     # print(auth_cookies)
    #     browser.close()
    # except:
    #     traceback.print_exc()
    #     browser.close()

    # with open('../data/sites.json') as sites_file:
    #     sites = json.load(sites_file)
    #     for site in sites:
    #         browser = Browser(home_url=site['home_url'], login_url=site['login_url'], register_url=site['register_url'], driver_path=PATH)
    #         browser.register()