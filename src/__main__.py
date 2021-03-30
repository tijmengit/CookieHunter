import traceback
from Browser import *
from CookieAuditor import *
from PrivacyAuditor import *
import json


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
                raise Exception(f'Could not register on page: {page}')
            document = browser.db.get_webpage(ref)
            if not document:
                raise Exception(f'Could not fetch document for: {ref}')

        # LOGIN
        creds = document['register_data']
        browser.login()
        if not browser.login_oracle():
            raise Exception(f'Could not login for: {page}')

        # COOKIE AUDIT
        cookie_auditor = CookieAuditor(browser)
        vulnerable = cookie_auditor.findVulnerableCookies()
        browser.db.update_web_page(ref, {"vulnerable": vulnerable})
        vulnerable_cookies = []
        if vulnerable['secure'] or vulnerable['httpOnly']:
            vulnerable_cookies = cookie_auditor.findAuthCookies()

        if not vulnerable_cookies:
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
    with open('../data/sites.json') as file:
        pages = json.load(file)
    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    privacy_auditor = PrivacyAuditor(PATH, ['--headless'])
    for page in pages:
        fullFlow(page, PATH, privacy_auditor)
