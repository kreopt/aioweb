import getpass


def run(*args, **kwargs):
    name = input('Enter user name: ')
    mail = input('Enter email: ')
    pass1 = getpass.getpass('Enter password: ')
    pass2 = getpass.getpass('Repeate password: ')

    if pass1 == pass2:
        from aioweb.contrib.auth.models.user import User
        u = User(username=name, email=mail, password=pass1, is_superuser=True, is_staff=True)
        u.save()
    else:
        print("passwords are not match")
