import traceback
from Browser import *
from CookieAuditor import *
from PrivacyAuditor import *
import json
import csv
import argparse
import sys

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
        print(f'========== REGISTRATION ==========')
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
    except KeyboardInterrupt as e:
        print(e)
        sys.exit(0)
    except:
        traceback.print_exc()
        browser.close()


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--domain','-d',
                           help='Specify a single domain such as: example.org', action='store', required=False)
    my_parser.add_argument('--alexa', '-a',
                           help="Use the alexa top 1m domain list", action='store_true', required=False)
    my_parser.add_argument('--start', '-s',
                           help='Start of index on the alexa list', action='store', type=int, required=False)
    args = my_parser.parse_args()

    PATH = os.getenv(
        "LOCALAPPDATA") + "/ChromeDriver/chromedriver" if platform.system() == "Windows" else "/usr/local/sbin/chromedriver"
    privacy_auditor = PrivacyAuditor(PATH, ['--headless'])
    print('########### COOKIE HUNTER \U0001F36A ###########')
    if args.alexa or type(args.start)==int:
        with open('../data/top-1m.csv') as sites_file:
            sites = csv.reader(sites_file, delimiter=',')
            line_count=0
            if type(args.start)==int and args.start>=0:
                start_at = args.start
            else:
                start_at = 0
            for row in sites:
                if line_count < start_at:
                    line_count += 1
                else:
                    page = {
                        'home_url':"https://"+row[1],
                        'login_url': None,
                        'register_url':None
                    }
                    try:
                        fullFlow(page, PATH, privacy_auditor)
                    except Exception as e:
                        print(e)
    elif type(args.domain)==str:
        page = {
            'home_url': "https://" + args.domain,
            'login_url': None,
            'register_url': None
        }
        try:
            fullFlow(page, PATH, privacy_auditor)
        except Exception as e:
            print(e)
    else:
        print("-> Using sites.json for domains")
        with open('../data/sites.json') as file:
            pages = json.load(file)
        for page in pages:
            fullFlow(page, PATH, privacy_auditor)
