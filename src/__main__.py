import traceback
from Browser import *
from CookieAuditor import *
from PrivacyAuditor import *
import json


def fullFlow(page, PATH, privacy_auditor):
    print(f'========== WEBSITE: {page["home_url"]} ==========')
    try:
        browser = Browser(page['home_url'], page['login_url'], page['register_url'], PATH)
        ref = browser.identifier
        document = browser.db.get_webpage(ref)
        if not document:
            raise Exception(f'Could not fetch document for: {ref}')

        # REGISTER
        print('')
        print(f'========== REGISTERATION ==========')
        register_in_db = False
        try:
            register_in_db = document['registered']
            print("-> We are already registered. Continue to Login. ")
        except Exception as e:
            pass
        if not register_in_db:
            print("-> Starting Register Process")
            registered = browser.register()
            if not registered:
                print("-> Registration not possible. Abort.")
                raise Exception(f'Could not register on page: {page}')
            document = browser.db.get_webpage(ref)
            print("-> Registration possible.")
            if not document:
                raise Exception(f'Could not fetch document for: {ref}')

        # LOGIN
        print('')
        print(f'========== LOGIN ==========')
        creds = document['register_data']
        print("-> Check if Login is possible.")
        browser.login()
        sleep(5)
        if not browser.login_oracle():
            print(f'-> ERROR: Login was not successful! Abort.')
            raise Exception(f'Could not login for: {page}')
        print(f'-> SUCCESS: Login was successful!')
        # COOKIE AUDIT
        print('')
        print('########### COOKIE AUDITOR ###########')
        cookie_auditor = CookieAuditor(browser)
        print(f'========== ALGORITHM 1: DETECT VULNERABLE COOKIES ==========')
        print(f'-> Check if there are vulnerable cookies regarding security attributes')
        vulnerable = cookie_auditor.findVulnerableCookies()
        print(f'-> Vulnerable Cookies [secure]: {vulnerable["secure"]} ')
        print(f'-> Vulnerable Cookies [httpOnly]: {vulnerable["httpOnly"]}')
        browser.db.update_web_page(ref, {"vulnerable": vulnerable})
        vulnerable_cookies = []
        if vulnerable['secure'] or vulnerable['httpOnly']:
            print(f'-> SUCCESS: We found vulnerable Cookies! Continue to Algorithm 2.')
            print(f'========== ALGORITHM 2: DETECT AUTHENTICATION COOKIES ==========')
            vulnerable_cookies = cookie_auditor.findAuthCookies()
            if vulnerable_cookies:
                print(f'-> SUCCESS: Authentication Cookie Combinations found!')
                print(f'Cookie Combinations: {vulnerable_cookies}')
        if not vulnerable_cookies:
            print(f'-> ERROR: Authentication Cookie Combinations not found!')
            browser.db.update_web_page(ref, {"leaks": []})
            return
        browser.close()

        # PRIVACY AUDIT
        print('')
        leaks = privacy_auditor.audit(page['home_url'], vulnerable_cookies[0], creds)
        browser.db.update_web_page(ref, {"leaks": leaks})

    except:
        traceback.print_exc()
        browser.close()


if __name__ == "__main__":
    with open('../data/sites.json') as file:
        pages = json.load(file)
    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "../chromedriver"
    privacy_auditor = PrivacyAuditor(PATH, ['--headless'])
    print('########### COOKIE HUNTER \U0001F36A ###########')
    for page in pages:
        fullFlow(page, PATH, privacy_auditor)
