
import sys
import traceback
from CookieHunter.src.Browser import *
from CookieHunter.src.CookieAuditor import *
import csv

if __name__ == "__main__":
    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    with open('../data/top-1m.csv') as sites_file:
        sites = csv.reader(sites_file, delimiter=',')
        line_count=0
        start_at = 10026
        for row in sites:
            if line_count < start_at:
                line_count += 1
            else:
                home_url = "https://"+row[1]
                browser = Browser(home_url=home_url, login_url=None, register_url=None, driver_path=PATH)
                browser.register()


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



