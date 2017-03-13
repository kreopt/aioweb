import os
import shutil

from framework import settings


def run(*args, **kwargs):
    DEST_DIR = os.path.join(settings.BASE_DIR, 'static')
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
    for appName in settings.APPS:
        try:
            print(os.path.join(settings.BASE_DIR, appName, 'static'))
            shutil.copytree(os.path.join(settings.BASE_DIR, appName, 'static'), DEST_DIR)
        except (OSError, FileNotFoundError) as exc:
            # traceback.print_exc()
            print("fail")
