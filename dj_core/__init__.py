from __future__ import absolute_import, print_function, unicode_literals

from pkg_resources import get_distribution

try:
    from dj_core import celery  # NOQA pre-import needed for alpine
except ImportError:
    pass
from dj_core import storage  # NOQA pre-import needed for alpine


__version__ = get_distribution('dj_core').version

default_app_config = 'dj_core.apps.DjCoreConfig'
