def create_synonyms(word_list):
    new_list = []
    for word in word_list:
        new_list.append(word.capitalize())
        if ' ' in word:
            new_list.append(__cap(word))
            new_list.append(__up(word))
        else:
            new_list.append(word.upper())
    word_list.extend(new_list)
    return


def __cap(word):
    tmp_list = []
    words = word.split(' ')
    for w in words:
        tmp_list.append(w.capitalize())
    word = ' '.join(tmp_list)
    return word


def __up(word):
    tmp_list = []
    words = word.split(' ')
    for w in words:
        tmp_list.append(w.upper())
    word = ' '.join(tmp_list)
    return word


def getSynonyms() -> dict:
    synonyms = {"email": ['user_email', 'email', 'e_mail', 'useremail', 'userEmail', 'mail', 'uemail',
                          'User_email', 'E_mail', 'UserEmail', 'Mail', 'Uemail',
                          'User_email_address', 'Email_address', 'email_address', 'emailadress',
                          'UserEmailAddress', 'Email address', 'Email Address', 'EMAIL',
                          'MailAdress', 'User Email', 'E-mail Address', 'e-mail address', 'Email address',
                          'User Email Address', 'User email address'
                          ], "password": ['user_password', 'password', 'pword', 'userpassword', 'userpwd', 'pwd', 'PWD',
                                          'u_password', 'passw', 'p_word', 'UserPassword', 'UserPwd', 'Pwd', 'pass',
                                          'Password',
                                          'User Password', 'Passwd', 'ConfirmPasswd', 'Confirm Password',
                                          'Confirm password',
                                          'onfirm Password', 'confirm password', 'CnfrmPsswrd', 'ConfirmPwd',
                                          'CnfrmPwd',
                                          'Re-enter Password', 'Password Confirm'
                                          ],
                "name": ['name_first', 'name', 'first_name', 'firstname', 'First_Name', 'f_name', 'firstName',
                         'User_efirstname', 'First_name', 'first_Name', 'NAME', 'F_NAME', 'FName',
                         'fname_', '_firstname', 'fullname', 'full_name', 'user_first_name', 'First Name',
                         'first name',
                         'nc_firstname', 'nc_firstname_required', 'First name', 'Name',

                         'last_name', 'lastname', 'last_Name', 'l_name', 'lastName',
                         'User_elastname', 'last_name', 'Last_Name', 'l_NAME', 'lName',
                         'lname_', '_lastname', 'user_last_name', 'Last Name', 'Last name', 'last name',
                         'nc_lastname', 'nc_lastname_required'

                         ], "username": ['username', 'uname', 'user_id', 'user_name', 'uName', 'u_Name', 'UserName',
                                         'user_name_new', 'new_username', 'user_username', 'user_username',
                                         'user[username]',
                                         'Username', 'nc_username', 'nc_username_required', 'Gebruikersnaam'
                                         ], 'cookie-accept': ['accept', 'confirm', 'choice', 'accept all cookies',
                                                              'I accept', "I Consent", "allow all cookies", "accept all"],
                'register': ['register', 'registration', 'sign up', 'signup', 'createuser', 'create user'],
                'login': ['login', 'log-in', 'log in']}

    create_synonyms(synonyms['cookie-accept'])
    create_synonyms(synonyms['register'])
    create_synonyms(synonyms['login'])
    return synonyms


def getCredentials(identifier: str) -> dict:
    return {"email": f'cookiehunterproject+{identifier}@gmail.com', "password": "passwordRandom123!",
            "name": "Janssen", "username": "CookieHunter007"}


def language_whitelist() -> dict:
    languages = ["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "ceb", "co", "cs", "cy", "da", "de", "el", "en",
                 "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl", "gu", "ha", "haw", "hi", "hmn", "hr",
                 "ht", "hu", "hy", "id", "ig", "is", "it", "iw", "ja", "jv", "ka", "kk", "km", "kn", "ko", "ku", "ky",
                 "la", "lb", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no",
                 "ny", "or", "pa", "pl", "ps", "pt", "ro", "ru", "rw", "sd", "si", "sk", "sl", "sm", "sn", "so", "sq",
                 "sr", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "ug", "uk", "ur", "uz",
                 "vi", "xh", "yi", "yo", "zh-CN", "zh-TW", "zu"]
    languageDict = {}
    for lang in languages:
        languageDict[lang] = "en"
    return languageDict


selenium_prefs = {
    "profile.default_content_setting_values.notifications": 2,
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.popups": 2,
    "profile.managed_default_content_settings.stylesheets": 2,
    "translate_whitelists": language_whitelist(),
    "translate": {"enabled": "true"}
}
