import importlib
import traceback

from framework.conf import settings

def setup_routes(app):
    for appName in settings.APPS:
        try:
            mod = importlib.import_module("%s.urls" % appName)
            setup_url = getattr(mod, 'setup_url')
            if setup_url:
                setup_url(app.router)
        except (ImportError, AttributeError) as e:
            traceback.print_exc()
