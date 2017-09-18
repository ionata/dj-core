from __future__ import absolute_import, print_function, unicode_literals

import os
from collections import OrderedDict
from importlib import import_module

from django.apps import apps
from django.utils.module_loading import module_has_submodule
from environ import Env


class Undefined(object):
    def __repr__(self):
        return '<{0}>'.format(self.__class__.__name__)


class EmailList(list):
    def __init__(self, value='', *args, **kwargs):
        super(EmailList, self).__init__(*args, **kwargs)
        self += [x.split(':') for x in value.split(',') if x]


class DjCoreEnv(Env):
    env_prefix = 'DJCORE_'

    def prefix(self, key):
        return self.env_prefix + key

    def __init__(self, **scheme):
        super(DjCoreEnv, self).__init__(**scheme)
        self.scheme = {self.prefix(key): val for key, val in scheme.items()}

    def get_value(self, var, *args, **kwargs):  # pylint: disable=arguments-differ
        return super(DjCoreEnv, self).get_value(self.prefix(var), *args, **kwargs)

    @classmethod
    def parse_value(cls, value, cast):
        if isinstance(cast, EmailList):
            return cast(value)
        return super(DjCoreEnv, cls).parse_value(value, cast)


def get_app_modules():
    """ From wagtail.utils
    Generator function that yields a module object for each installed app
    yields tuples of (app_name, module)
    """
    for app in apps.get_app_configs():
        yield app.name, app.module


def get_app_submodules(submodule_name):
    """ From wagtail.utils
    Searches each app module for the specified submodule
    yields tuples of (app_name, module)
    """
    for name, module in get_app_modules():
        if module_has_submodule(module, submodule_name):
            yield name, import_module('%s.%s' % (name, submodule_name))


def get_root_url():
    """Determine the root URL for the site."""
    from django.conf import settings
    return settings.DJCORE.SITE_URL


def as_absolute(url):
    return get_root_url() + url


def import_from_string(value):
    """Copy of rest_framework.settings.import_from_string"""
    value = value.replace('-', '_')
    try:
        module_path, class_name = value.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as ex:
        raise ImportError("Could not import '{}'. {}: {}.".format(
            value, ex.__class__.__name__, ex))


class AttrDict(OrderedDict):
    def __getattr__(self, key):
        if key[0] != '_':
            return self[key]
        return super(AttrDict, self).__getattr__(key)

    def __setattr__(self, key, val):
        if key[0] != '_':
            self[key] = val
        return super(AttrDict, self).__setattr__(key, val)


def get_resolved_settings_dict(settings_module=None):
    from django.conf import ENVIRONMENT_VARIABLE, Settings
    settings = Settings(settings_module or os.environ[ENVIRONMENT_VARIABLE])
    return {x: getattr(settings, x) for x in dir(settings) if x[0] != '_'}


def settings_diff(conf_name, show_added=False):
    other = get_resolved_settings_dict(conf_name)
    existing = get_resolved_settings_dict()
    extra = other if show_added else existing
    base = existing if show_added else other
    return {
        k: v for k, v in extra.items()
        if extra['is_overridden'](k) and (k not in base or base[k] != v)
    }
