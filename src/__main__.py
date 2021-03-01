
import sys
import traceback
from src.Browser import *
from src.CookieAuditor import *

if __name__ == "__main__":
    home_url = ""
    login_url = ""
    register_url = "https://www.amazon.nl/ap/register?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.nl%2F%3F_encoding%3DUTF8%26ref_%3Dnav_newcust&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=nlflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
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
