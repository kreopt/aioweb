import re


def sub_phone(raw):
    if raw is None:
        return None
    r = re.sub('[^0-9]', '', raw)[-10:]
    if not len(r):
        return None
    return r


def sub_email_or_phone(raw):
    username = re.sub('[^A-Za-z0-9-_@.]', '', raw)

    if '@' not in username:
        return sub_phone(username)

    return username
