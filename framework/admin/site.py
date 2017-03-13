MODELS = {}

def register(model):
    if not hasattr(model, 'Admin'):
        class Admin:
            __id_field__ = 'id'
        setattr(model, 'Admin', Admin)
    if not hasattr(model.Admin, '__id_field__'):
        setattr(model.Admin, '__id_field__', 'id')
    MODELS[model.__name__.lower()] = model