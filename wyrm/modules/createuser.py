import getpass
import sys
import os

brief = "create new user"
aliases = ["c", "shell"]


def execute(argv, argv0, engine):
    import lib, importlib, re
    import code
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    from aioweb import settings
    sys.path.append(settings.BASE_DIR)
    # Initialize Orator ORM
    lib.init_orator(settings)

    from aioweb.contrib.auth.models.user import User

    for i in range(0, 3):
        name = input('Enter user name: ')
        mail = input('Enter email: ')
        pass1 = getpass.getpass('Enter password: ')
        pass2 = getpass.getpass('Repeat password: ')

        if pass1 == pass2:
            from aioweb.contrib.auth.models.user import User
            u = User(username=name, email=mail, password=pass1)
            u.save()
            break
        else:
            print("passwords does not match\n\n")
