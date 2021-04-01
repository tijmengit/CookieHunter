import traceback
from Browser import *
from CookieAuditor import *
from PrivacyAuditor import *
import json
import csv
import sys

def fullFlow(page, PATH, privacy_auditor):

    try:
        browser = Browser(page['home_url'], page['login_url'], page['register_url'], PATH)
        ref = browser.identifier
        document = browser.db.get_webpage(ref)
        if not document:
            raise Exception(f'Could not fetch document for: {ref}')

        # REGISTER
        register_in_db = False
        try:
            register_in_db = document['registered']
        except Exception as e:
            pass
        if not register_in_db:
            registered = browser.register()
            if not registered:
                raise Exception(f'Could not register on page: ' +page["home_url"])
            document = browser.db.get_webpage(ref)
            if not document:
                raise Exception(f'Could not fetch document for: {ref}')

        # LOGIN
        creds = document['register_data']
        browser.login()
        sleep(1)
        if not browser.login_oracle():
            raise Exception(f'Could not login for: ' +page["home_url"] )
        print("Can login to page: " + page['home_url'])
        # COOKIE AUDIT
        print('########### COOKIE AUDITOR ###########')
        cookie_auditor = CookieAuditor(browser)
        vulnerable = cookie_auditor.findVulnerableCookies()
        browser.db.update_web_page(ref, {"vulnerable": vulnerable})
        vulnerable_cookies = []
        if vulnerable['secure'] or vulnerable['httpOnly']:
            vulnerable_cookies = cookie_auditor.findAuthCookies()

        if not vulnerable_cookies:
            print("No vulnerable cookies found.")
            browser.db.update_web_page(ref, {"leaks": []})
            return
        browser.close()

        # PRIVACY AUDIT
        leaks = privacy_auditor.audit(page['home_url'], vulnerable_cookies[0], creds)
        browser.db.update_web_page(ref, {"leaks": leaks})

    except:
        traceback.print_exc()
        browser.close()


if __name__ == "__main__":
    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    privacy_auditor = PrivacyAuditor(PATH, ['--headless'])
    # this needs to be replaced with a getter for all pages we want to inspect
    # pages = [
    #     {
    #         'home_url': 'https://www.goodreads.com',
    #         'login_url': 'https://www.goodreads.com/user/sign_in',
    #         'register_url': 'https://www.goodreads.com/user/sign_up'
    #     }
    # ]
    # with open('../data/top-1m.csv') as sites_file:
    #     sites = csv.reader(sites_file, delimiter=',')
    #     line_count=0
    #     start_at = int(sys.argv[1])
    #     for row in sites:
    #         if line_count < start_at:
    #             line_count += 1
    #         else:
    #             page = {
    #                 'home_url':"https://"+row[1],
    #                 'login_url': None,
    #                 'register_url':None
    #             }
    #             try:
    #                 fullFlow(page, PATH, privacy_auditor)
    #             except Exception as e:
    #                 print(e)


    with open('../data/sites.json') as file:
        pages = json.load(file)
    index =0
    for page in pages:
        if index ==1:
            fullFlow(page, PATH, privacy_auditor)
        index +=1

