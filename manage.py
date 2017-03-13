import asyncio
import getpass
import os
import shutil
import sys
import traceback

os.environ.setdefault("SETTINGS_MODULE", "settings")

import framework
from framework.conf import settings


def create(*args, **kwargs):
    pass

def collectstatic(*args, **kwargs):
    DEST_DIR = os.path.join(settings.BASE_DIR, 'static')
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
    for appName in settings.APPS:
        try:
            print(os.path.join(settings.BASE_DIR, appName, 'static'))
            shutil.copytree(os.path.join(settings.BASE_DIR, appName, 'static'), DEST_DIR)
        except (OSError, FileNotFoundError) as exc:
            traceback.print_exc()


def makemigration(app_name, migration_name, *args, **kwargs):
    os.system("orator make:migration %s -p %s/migrations/ %s" % (migration_name,
                                                         os.path.join(settings.BASE_DIR, 'app', app_name.replace('.', '/')),
                                                         ''.join(args))
              )


def rollback(app_name, *args, **kwargs):
    os.system("orator migrate:rollback -c %s/settings.py -p %s/migrations/" % (
        settings.BASE_DIR,
        os.path.join(settings.BASE_DIR, 'app', app.replace('.', '/'))))


def migrate(app_name=None, *args, **kwargs):
    if app_name:
        apps = [app_name]
    else:
        apps = settings.APPS

    for app in apps:
        os.system("orator migrate -c %s/settings.py -p %s/migrations/" % (
            settings.BASE_DIR,
            os.path.join(settings.BASE_DIR, 'app', app.replace('.','/'))
        ))


def createsuperuser():
    name = input('Enter user name:')
    mail = input('Enter email:')
    pass1 = getpass.getpass('Enter password:')
    pass2 = getpass.getpass('Repeate password:')

    if pass1 == pass2:
        from framework.auth.models.user import User
        u = User(username=name, email=mail, password=pass1, is_superuser=True, is_staff=True)
        u.save()
    else:
        print("passwords are not match")

def createprofile():
    username = input('Enter user name:')
    from framework.auth.models.user import User
    from app.cabinet.models.user_profile import UserProfile

    u = User.where('username', username).first_or_fail()
    p = UserProfile(user_id=u.id)
    p.save()


def runserver():
    pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = framework.Application(loop=loop, middlewares=[])
    app = loop.run_until_complete(app.setup())

    if len(sys.argv) >= 1:
        try:
            mname = sys.argv[1]
            args = sys.argv[2:]
            globals()[mname](*args)
        except KeyError:
            print("no such method: %s" % sys.argv[1])
