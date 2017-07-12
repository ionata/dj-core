dj-core
=======

A self-contained and extensible django environment.

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


Disabling optional packages:
----------------------------

django-anymail
~~~~~~~~~~~~~~
set the environment variable `DJCORE_EMAIL_BACKEND` to your backend of choice

django-debug-toolbar[-line-profiler]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
set the environment variable `DJCORE_USE_DJDT` to `0` or `False`

django-minimal-user
~~~~~~~~~~~~~~~~~~~
set the environment variable `DJCORE_AUTH_USER_MODEL` to your model of choice

django-storages
~~~~~~~~~~~~~~~
set the environment variable `DJCORE_DEFAULT_FILE_STORAGE` to your engine of choice
set the environment variable `DJCORE_STATICFILES_STORAGE` to your engine of choice

Note that the default is to not provide access to the underlying filesystem.
If you require that, update your settings as applicable
