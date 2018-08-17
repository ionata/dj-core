try:
    from dj_core import celery  # NOQA pre-import for Celery to work
except ImportError:
    pass
from dj_core import storage  # NOQA pre-import needed for alpineVERSION = '0.2.0'

VERSION = '0.2.0'
default_app_config = 'dj_core.apps.DjCoreConfig'
