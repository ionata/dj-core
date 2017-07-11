# pylint: disable=not-callable
from __future__ import absolute_import, print_function, unicode_literals

from importlib import import_module

from django.utils import six
from environ import Env

from .utils import AttrDict


class BaseConfig(object):
    defaults = {
        'DJCORE_APP_NAME': (str, 'dj_core'),
        'DJCORE_APP_CONF': (str, ''),
        'DJCORE_DEBUG': (bool, False),
    }

    def __init__(self, *args, **kwargs):
        self._env = None
        self.settings = self.get_settings()
        super(BaseConfig, self).__init__(*args, **kwargs)

    @staticmethod
    def can_import(app_name):
        try:
            import_module(app_name)
        except ImportError:
            return False
        return True

    @property
    def env(self):
        if self._env is None:
            self._env = Env(**self.types)
        return self._env

    @property
    def app_name(self):
        return self.env('DJCORE_APP_NAME')

    @property
    def app_conf(self):
        val = self.env('DJCORE_APP_CONF')
        if val == '':
            val = '{}.config.Config'.format(self.app_name)
        module, conf = val.rsplit('.', 1)
        return getattr(import_module(module), conf)

    @property
    def debug(self):
        return self.env('DJCORE_DEBUG')

    @property
    def types(self):
        return {k: (type(v), v) for k, v in self.get_defaults().items()}

    def get_defaults(self):  # pylint: disable=no-self-use
        return self.defaults

    def get_settings(self):  # pylint: disable=no-self-use
        return AttrDict({'DEBUG': self.env('DJCORE_DEBUG')})


class Config(BaseConfig):
    defaults = {
        'simple': {
            'DJCORE_ALLOWED_HOSTS': ['localhost'],
            'DJCORE_ANONYMOUS_USER_ID': -1,
            'DJCORE_AUTHENTICATION_BACKENDS': ['django.contrib.auth.backends.ModelBackend'],
            'DJCORE_AUTH_USER_MODEL': 'minimal_user.User',
            'DJCORE_BROKER_URL': 'redis://',
            'DJCORE_BROKER_TRANSPORT_OPTIONS': {'visibility_timeout': 3600},  # 1 hour.
            'DJCORE_CELERY_APP_NAME': '$DJCORE_APP_NAME',
            'DJCORE_CELERY_RESULT_BACKEND': '$DJCORE_BROKER_URL',
            'DJCORE_CORS_ORIGIN_ALLOW_ALL': False,
            'DJCORE_CORS_ORIGIN_WHITELIST': '$DJCORE_ALLOWED_HOSTS',
            'DJCORE_CSRF_COOKIE_PATH': '/backend/',
            'DJCORE_CSRF_COOKIE_SECURE': True,
            'DJCORE_CSRF_TRUSTED_ORIGINS': '$DJCORE_CORS_ORIGIN_WHITELIST',
            'DJCORE_EMAIL_BACKEND': 'anymail.backends.mailgun.MailgunBackend',
            'DJCORE_INTERNAL_IPS': ['127.0.0.1'],
            'DJCORE_LANGUAGE_CODE': 'en-AU',
            'DJCORE_LOGIN_URL': '/backend/login/',
            'DJCORE_MEDIA_URL': '/assets/media/',
            'DJCORE_ROOT_URLCONF': 'dj_core.urls',
            'DJCORE_SECRET_KEY': '',
            'DJCORE_SESSION_COOKIE_PATH': '/backend/',
            'DJCORE_SESSION_COOKIE_SECURE': True,
            'DJCORE_SITE_ID': 1,
            'DJCORE_STATIC_URL': '/assets/static/',
            'DJCORE_TIME_ZONE': 'UTC',
            'DJCORE_USE_I18N': True,
            'DJCORE_USE_L10N': True,
            'DJCORE_USE_TZ': True,
            'DJCORE_WSGI_APPLICATION': 'dj_core.wsgi.application',
        },
        'djcore': {
            'DJCORE_ADMIN_ENABLED': True,
            'DJCORE_ADMIN_USER': {'email': '', 'password': ''},
            'DJCORE_FRONTEND_URL': 'https://localhost',
            'DJCORE_SITE_NAME': '$DJCORE_APP_NAME',
            'DJCORE_SITE_URL': 'https://localhost',
            'DJCORE_USE_DJDT': False,
            'DJCORE_WHITELIST_SITE_URL': True,
        },
        'complex': {
            'DJCORE_ADMINS': [],
            'DJCORE_MANAGERS': [],
        },
        'dev': {
            'DJCORE_ADMIN_USER': {'email': 'test@example.com', 'password': 'password'},
            'DJCORE_ALLOWED_HOSTS': ['*'],
            'DJCORE_BROKER_URL': 'redis://redis',
            'DJCORE_CELERY_RESULT_BACKEND': 'redis://redis',
            'DJCORE_CORS_ORIGIN_ALLOW_ALL': True,
            'DJCORE_CSRF_COOKIE_SECURE': False,
            'DJCORE_DATABASE_URL': 'postgis://django:django@db:5432/django',
            'DJCORE_EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
            'DJCORE_SESSION_COOKIE_SECURE': False,
            'DJCORE_USE_DJDT': True,
        },
    }

    @property
    def djdt_enabled(self):
        return self.debug and self.env('DJCORE_USE_DJDT')

    @property
    def site_url(self):
        return six.moves.urllib.parse.urlparse(self.env('DJCORE_SITE_URL'))  # pylint: disable=no-member

    def get_defaults(self):
        defaults = super(Config, self).get_defaults()
        defaults.update(self.defaults['simple'])
        defaults.update(self.defaults['djcore'])
        defaults.update(self.defaults['complex'])
        if self.debug:
            defaults.update(self.defaults['dev'])
        return defaults

    def get_settings(self):
        settings = super(Config, self).get_settings()
        settings.update(self.get_core_settings())
        settings.DJCORE = self.get_djcore_settings(settings)
        settings.DATABASES = self.get_databases(settings)
        settings.INSTALLED_APPS = self.get_installed_apps(settings)
        settings.MIDDLEWARE = self.get_middleware(settings)
        settings.TEMPLATES = self.get_templates(settings)
        settings.update(self.get_email_settings(settings))
        return settings

    def get_core_settings(self):
        conf = {self.env(key) for key in self.defaults['simple']}
        conf.ALLOWED_HOSTS += conf.INTERNAL_IPS
        if self.env('DJCORE_WHITELIST_SITE_URL'):
            conf.ALLOWED_HOSTS += self.site_url.netloc
            conf.CORS_ORIGIN_WHITELIST += self.site_url.netloc
            conf.CSRF_TRUSTED_ORIGINS += self.site_url.netloc
        if self.djdt_enabled:
            conf.DEBUG_TOOLBAR_CONFIG = {
                'SHOW_COLLAPSED': True,
                'SHOW_TOOLBAR_CALLBACK': lambda request: True
            }
        return conf

    def get_djcore_settings(self, settings):  # pylint: disable=unused-argument
        conf = AttrDict({self.env(key) for key in self.defaults['djcore']})
        conf.update({
            'SITE_DOMAIN': self.site_url.netloc,
            'APP_NAME': self.env('DJCORE_APP_NAME'),
            'APP_CONF': self.env('DJCORE_APP_CONF'),
        })
        return conf

    def get_databases(self, settings):  # pylint: disable=unused-argument
        return {'default': self.env.db('DJCORE_DATABASE_URL')}

    def get_installed_apps(self, settings):
        return [
            settings.DJCORE.APP_NAME,
            'dj_core',

            # Django apps
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.sites',
        ] + [x for x in [
            'minimal_user',
            'anymail',
            'django_extensions',
            'django_storages',
        ] if self.can_import(x)] + ([
            'debug_toolbar',
            'debug_toolbar_line_profiler',
        ] if self.djdt_enabled else [])

    def get_middleware(self, settings):  # pylint: disable=unused-argument
        return ([
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        ] if self.djdt_enabled else []) + [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'django.middleware.security.SecurityMiddleware',
        ]

    def get_templates(self, settings):  # pylint: disable=no-self-use,unused-argument
        return [{
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

    def get_email_settings(self, settings):
        conf = AttrDict({
            'EMAIL_SUBJECT_PREFIX': self.env.str(
                'DJCORE_EMAIL_SUBJECT_PREFIX',
                '[Django - {}] '.format(settings.DJCORE.APP_NAME)),
            'ADMINS': [x.split(':') for x in self.env('DJCORE_ADMINS')],
            'MANAGERS': [x.split(':') for x in self.env('DJCORE_MANAGERS')],
            'DEFAULT_FROM_EMAIL': self.env.str(
                'DJCORE_EMAIL_FROM',
                'no-reply@{}'.format(self.site_url.hostname)),
        })
        if settings.EMAIL_BACKEND == 'anymail.backends.mailgun.MailgunBackend':
            conf.ANYMAIL = {
                key: self.env.str('DJCORE_{}'.format(key))
                for key in ['MAILGUN_API_KEY', 'MAILGUN_SENDER_DOMAIN']
            }
        return conf
