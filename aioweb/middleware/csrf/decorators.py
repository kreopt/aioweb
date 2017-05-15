from aioweb.util import get_own_properties


def csrf_exempt(fn):
    setattr(fn, 'csrf_disabled', True)
    return fn


def csrf_protect(fn):
    setattr(fn, 'csrf_disabled', False)
    return fn


def disable_csrf(only=tuple(), exclude=tuple()):
    def decorate(cls):
        for name, member in get_own_properties(cls):
            if name not in exclude and (name in only or len(only) == 0) and not hasattr(member, 'csrf_disabled'):
                setattr(member, 'csrf_disabled', True)
        return cls

    return decorate
