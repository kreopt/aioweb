def setup_middlewares(app, middlewares):
    for middleware in middlewares:
        app.middlewares.append(middleware)