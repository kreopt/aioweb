from aioweb.middleware.error_mailer import error_mailer
from aioweb.middleware.method_override import method_override
from aioweb.middleware.is_ajax import is_ajax_middleware


def setup_middlewares(app, middlewares):
    app.middlewares.append(method_override)
    app.middlewares.append(is_ajax_middleware)
    app.middlewares.append(error_mailer)

    for middleware in middlewares:
        app.middlewares.append(middleware)
