# dj-core
[![PyPI](https://img.shields.io/pypi/pyversions/dj-core.svg)](https://pypi.org/project/dj-core/)
[![PyPI](https://img.shields.io/pypi/v/dj-core.svg)](https://pypi.org/project/dj-core/)
[![Updates](https://pyup.io/repos/github/ionata/dj-core/shield.svg)](https://pyup.io/repos/github/ionata/dj-core/)

## A self-contained and extensible django environment.
The default configuration makes use of the following optional packages:
- django-anymail[mailgun]
- django-debug-toolbar
- django-debug-toolbar-line-profiler
- django-minimal-user
- django-storages

The default configuration also configures the following, but does not require them:
- django-extensions
- django-cors-headers
- celery[redis]

## Disabling optional packages:
Override the following environment variables:
- django-anymail: `DJCORE_EMAIL_BACKEND`
- django-debug-toolbar[-line-profiler]: `DJCORE_USE_DJDT`
- django-minimal-user: `DJCORE_AUTH_USER_MODEL`
- django-storages: `DJCORE_DEFAULT_FILE_STORAGE`, `DJCORE_STATICFILES_STORAGE`
