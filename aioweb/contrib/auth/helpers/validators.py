import re


def sub_phone(raw):
    return re.sub('[^0-9]', '', raw)[-10:]


def sub_email_or_phone(raw):
    username = re.sub('[^A-Za-z0-9-_@.]', '', raw)

    if '@' not in username:
        return sub_phone(username)

    return username
