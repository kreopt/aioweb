MODELS = {}

def register(model):
    MODELS[model.__name__.lower()] = model