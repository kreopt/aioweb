"""
Settings and configuration for Django.

Values will be read from the module specified by the DJANGO_SETTINGS_MODULE environment
variable, and then from django.conf.global_settings; see the global settings file for
a list of all possible variables.
"""

import importlib
import os
import time
from . import global_settings

ENVIRONMENT_VARIABLE = "AIOWEB_SETTINGS_MODULE"


class ImproperlyConfigured(BaseException):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class BaseSettings(object):
    """
    Common logic for settings whether set by a module or by the user.
    """

    def __setattr__(self, name, value):
        if name in ("MEDIA_URL", "STATIC_URL") and value and not value.endswith('/'):
            raise ImproperlyConfigured("If set, %s must end with a slash" % name)
        object.__setattr__(self, name, value)


class Settings(BaseSettings):
    def __init__(self, settings_module):
        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        mod = importlib.import_module(self.SETTINGS_MODULE)

        tuple_settings = (
            "APPS",
        )
        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                if (setting in tuple_settings and
                        not isinstance(setting_value, (list, tuple))):
                    raise ImproperlyConfigured("The %s setting must be a list or a tuple. " % setting)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            'cls': self.__class__.__name__,
            'settings_module': self.SETTINGS_MODULE,
        }


class UserSettingsHolder(BaseSettings):
    """
    Holder for user configured settings.
    """
    # SETTINGS_MODULE doesn't make much sense in the manually configured
    # (standalone) case.
    SETTINGS_MODULE = None

    def __init__(self, default_settings):
        """
        Requests for configuration variables not in this class are satisfied
        from the module specified in default_settings (if possible).
        """
        self.__dict__['_deleted'] = set()
        self.default_settings = default_settings

    def __getattr__(self, name):
        if name in self._deleted:
            raise AttributeError
        return getattr(self.default_settings, name)

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super(UserSettingsHolder, self).__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super(UserSettingsHolder, self).__delattr__(name)

    def __dir__(self):
        return sorted(
            s for s in list(self.__dict__) + dir(self.default_settings)
            if s not in self._deleted
        )

    def is_overridden(self, setting):
        deleted = (setting in self._deleted)
        set_locally = (setting in self.__dict__)
        set_on_default = getattr(self.default_settings, 'is_overridden', lambda s: False)(setting)
        return (deleted or set_locally or set_on_default)

    def __repr__(self):
        return '<%(cls)s>' % {
            'cls': self.__class__.__name__,
        }


settings = Settings(os.environ.get(ENVIRONMENT_VARIABLE))
