from __future__ import absolute_import, print_function, unicode_literals

from collections import OrderedDict
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.utils.module_loading import module_has_submodule


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
    return settings.DJCORE.SITE_URL


def as_absolute(url):
    return get_root_url() + url


def import_from_string(value):
    """
    Copy of rest_framework.settings.import_from_string
    Does not require a setting_name for the exception message"""
    try:
        # Nod to tastypie's use of importlib.
        parts = value.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
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
