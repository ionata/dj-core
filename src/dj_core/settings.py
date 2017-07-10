# pylint: disable=not-callable
from __future__ import absolute_import, print_function, unicode_literals

from os import path

from django.utils import six
from environ import Env

from .utils import AttrDict


class Settings(object):
    types = {}

    def __init__(self, *args, **kwargs):
        self._env = None
        self.settings = self.get_defaults()
        self.settings.update(self.get_settings())
        self.apply()
        super(Settings, self).__init__(*args, **kwargs)

    @property
    def env(self):
        if self._env is None:
            self._env = Env(**self.types)
        return self._env

    def get_defaults(self):  # pylint: disable=no-self-use
        return AttrDict()

    def get_settings(self):  # pylint: disable=no-self-use
        return AttrDict()

    def apply(self):
        globals().update(self.settings)


class DjCoreSettings(Settings):
    defaults = {
        'DJCORE_ADMINS': [],
        'DJCORE_ADMIN_ENABLED': True,
        'DJCORE_ALLOWED_HOSTS': [],
        'DJCORE_BROKER_URL': 'redis://',
        'DJCORE_CELERY_RESULT_BACKEND': '$DJCORE_BROKER_URL',
        'DJCORE_CORS_ORIGIN_ALLOW_ALL': False,
        'DJCORE_CORS_ORIGIN_WHITELIST': [],
        'DJCORE_CSRF_COOKIE_SECURE': True,
        'DJCORE_CSRF_TRUSTED_ORIGINS': [],
        'DJCORE_DEBUG': False,
        'DJCORE_EMAIL_BACKEND': "django.core.mail.backends.console.EmailBackend",
        'DJCORE_FRONTEND_URL': 'https://localhost',
        'DJCORE_MANAGERS': [],
        'DJCORE_SESSION_COOKIE_SECURE': True,
        'DJCORE_SITE_URL': 'https://localhost',
        'DJCORE_USE_DJDT': False,
    }
    debug_defaults = {
        'DJCORE_ALLOWED_HOSTS': ['*'],
        'DJCORE_BROKER_URL': 'redis://redis',
        'DJCORE_CELERY_RESULT_BACKEND': 'redis://redis',
        'DJCORE_CORS_ORIGIN_ALLOW_ALL': True,
        'DJCORE_CSRF_COOKIE_SECURE': False,
        'DJCORE_DATABASE_URL': 'postgis://django:django@db:5432/django',
        'DJCORE_SESSION_COOKIE_SECURE': False,
        'DJCORE_SITE_URL': 'https://localhost',
        'DJCORE_USE_DJDT': True,
    }
    types = {k: (type(v), v) for k, v in defaults.items()}

    @property
    def debug(self):
        return self.env('DJCORE_DEBUG')

    def get_defaults(self):
        defaults = self.defaults.copy()
        if self.debug:
            defaults.update(self.debug_defaults)
        return defaults

    def get_settings(self):
        settings = super(DjCoreSettings, self).get_settings()
        settings.update(self._get_core_settings())
        settings.DJCORE.update(self._get_djcore_settings(settings))
        settings.update(self._get_email_config(settings))
        settings.update(self._get_celery_config(settings))
        settings.update(self._get_auth_config(settings))
        self._apply_dev_settings(settings)
        return settings

    def _get_core_settings(self):
        new = AttrDict({'DJCORE': AttrDict()})
        new.SECRET_KEY = self.env.str('DJCORE_SECRET_KEY')
        new.DJCORE.APP_ROOT = path.abspath(path.dirname(globals()['__file__']))
        new.DJCORE.PROJECT_APP = path.split(new.DJCORE.APP_ROOT)[1]
        new.DJCORE.PROJECT_NAME = self.env.str('DJCORE_PROJECT_NAME', new.DJCORE.PROJECT_APP)
        new.DJCORE.VAR_ROOT = self.env.str('DJCORE_VAR_DIR')
        new.DJCORE.LOG_ROOT = path.join(new.DJCORE.VAR_ROOT, 'log')
        new.DJCORE.DOCUMENT_ROOT = path.join(new.DJCORE.VAR_ROOT, 'www')
        new.STATIC_ROOT = path.join(new.DJCORE.DOCUMENT_ROOT, 'static')
        new.MEDIA_ROOT = path.join(new.DJCORE.DOCUMENT_ROOT, 'media')
        new.INSTALLED_APPS = [
            # Our apps
            'minimal_user',
            'dj_core',

            # Django apps
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.sites',

            # Third party apps
            'anymail',
            'django_extensions',
        ]
        new.DJCORE.PROJECT_APPS = [new.DJCORE.PROJECT_APP]
        if new.DJCORE.get('DETECT_PROJECT_APPS', False):
            new.INSTALLED_APPS = new.DJCORE.PROJECT_APPS + new.INSTALLED_APPS

        new.MIDDLEWARE = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'django.middleware.security.SecurityMiddleware',
        ]

        new.TEMPLATES = [{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.template.context_processors.request',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }]

        new.ROOT_URLCONF = 'dj_core.urls'
        new.WSGI_APPLICATION = 'dj_core.wsgi.application'

        new.LANGUAGE_CODE = 'en-AU'
        new.TIME_ZONE = 'UTC'
        new.USE_I18N = True
        new.USE_L10N = True
        new.USE_TZ = True

        # URLs for assets
        new.ASSETS_URL = '/assets/'
        new.MEDIA_URL = new.ASSETS_URL + 'media/'
        new.STATIC_URL = new.ASSETS_URL + 'static/'

        new.INTERNAL_IPS = ['127.0.0.1']
        new.ALLOWED_HOSTS = ['localhost'] + new.INTERNAL_IPS
        new.ALLOWED_HOSTS.extend(self.env.list('DJCORE_ALLOWED_HOSTS', []))

        new.EMAIL_SUBJECT_PREFIX = '[Django - {}] '.format(new.DJCORE.PROJECT_NAME)
        new.ADMINS = [x.split(':') for x in self.env.list('DJCORE_ADMINS')]
        new.MANAGERS = [x.split(':') for x in self.env.list('DJCORE_MANAGERS')]
        new.DATABASES = {'default': self.env.db('DJCORE_DATABASE_URL')}
        return new

    def _get_djcore_settings(self, settings):
        url = six.moves.urllib.parse.urlparse(self.env.str('DJCORE_SITE_URL'))  # pylint: disable=no-member
        if url.port is not None:
            settings.DJCORE.site.hostname += ':{}'.format(url.port)
        return {
            'ADMIN_ENABLED': self.env('DJCORE_ADMIN_ENABLED'),
            'site': AttrDict({
                'name': self.env.str('DJCORE_SITE_NAME', settings.DJCORE.PROJECT_NAME),
                'domain': url.hostname,
                'url': url,
            }),
            'admin': AttrDict({
                'email': self.env.str('DJCORE_ADMIN_USER'),
                'password': self.env.str('DJCORE_ADMIN_PASS'),
            }),
            'USE_DJDT': self.env.bool('DJCORE_USE_DJDT')
        }

    def _get_email_config(self, settings):
        conf = AttrDict({
            'DEFAULT_FROM_EMAIL': self.env.str(
                'DJCORE_EMAIL_FROM', 'no-reply@{}'.format(settings.DJCORE.site.url)),
            'EMAIL_BACKEND': self.env.str('DJCORE_EMAIL_BACKEND')
        })
        if conf.EMAIL_BACKEND == 'anymail.backends.mailgun.MailgunBackend':
            conf.ANYMAIL = {
                key: self.env.str('DJCORE_{}'.format(key))
                for key in ['MAILGUN_API_KEY', 'MAILGUN_SENDER_DOMAIN']
            }
        return conf

    def _get_celery_config(self, settings):
        return {
            'CELERY_APP_NAME': settings.DJCORE.PROJECT_NAME,
            'BROKER_TRANSPORT_OPTIONS': {'visibility_timeout': 3600},  # 1 hour.
            'BROKER_URL': self.env('DJCORE_BROKER_URL'),
            'CELERY_RESULT_BACKEND': self.env('DJCORE_CELERY_RESULT_BACKEND'),
        }

    def _get_auth_config(self, settings):
        return {
            'ANONYMOUS_USER_ID': -1,
            'AUTHENTICATION_BACKENDS': ['django.contrib.auth.backends.ModelBackend'],
            'AUTH_USER_MODEL': 'minimal_user.User',
            'CSRF_TRUSTED_ORIGINS': (
                settings.ALLOWED_HOSTS
                + self.env('DJCORE_CSRF_TRUSTED_ORIGINS')),
            'SESSION_COOKIE_PATH': '/backend/',
            'CSRF_COOKIE_PATH': '/backend/',
            'LOGIN_URL': '/backend/login/',
            'SESSION_COOKIE_SECURE': self.env('DJCORE_SESSION_COOKIE_SECURE'),
            'CSRF_COOKIE_SECURE': self.env('DJCORE_CSRF_COOKIE_SECURE'),
        }

    def _apply_dev_settings(self, settings):
        if self.debug and settings.DJCORE.USE_DJDT:
            settings.INSTALLED_APPS += [
                'debug_toolbar',
                'debug_toolbar_line_profiler',
            ]
            settings.MIDDLEWARE = [
                'debug_toolbar.middleware.DebugToolbarMiddleware',
            ] + settings.MIDDLEWARE
            settings.DEBUG_TOOLBAR_CONFIG = {
                'SHOW_COLLAPSED': True,
                'SHOW_TOOLBAR_CALLBACK': lambda request: True
            }
