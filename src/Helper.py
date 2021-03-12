def create_synonyms(word_list):
    new_list = []
    for word in word_list:
        new_list.append(word.capitalize())
        if ' ' in word:
            new_list.append(cap(word))
            new_list.append(up(word))
        else:
            new_list.append(word.upper())
    word_list.extend(new_list)
    return


def cap(word):
    tmp_list = []
    words = word.split(' ')
    for w in words:
        tmp_list.append(w.capitalize())
    word = ' '.join(tmp_list)
    return word


def up(word):
    tmp_list = []
    words = word.split(' ')
    for w in words:
        tmp_list.append(w.upper())
    word = ' '.join(tmp_list)
    return word

def language_whitelist():
    languages = ["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "ceb", "co", "cs", "cy", "da", "de", "el", "en",
            "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl", "gu", "ha", "haw", "hi", "hmn", "hr",
            "ht", "hu", "hy", "id", "ig", "is", "it", "iw", "ja", "jv", "ka", "kk", "km", "kn", "ko", "ku", "ky",
            "la", "lb", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no",
            "ny", "or", "pa", "pl", "ps", "pt", "ro", "ru", "rw", "sd", "si", "sk", "sl", "sm", "sn", "so", "sq",
            "sr", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "ug", "uk", "ur", "uz",
            "vi", "xh", "yi", "yo", "zh-CN", "zh-TW", "zu"]
    dict = {}
    for l in languages:
        dict[l] = "en"
    return dict