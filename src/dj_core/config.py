# pylint: disable=not-callable
from __future__ import absolute_import, print_function, unicode_literals

from importlib import import_module
from os import path

from django.utils import six
from environ import Env

from .utils import AttrDict


def _can_import(app_name):
    try:
        import_module(app_name)
    except ImportError:
        return False
    return True


class BaseConfig(object):
    defaults = {
        'DJCORE_APP_NAME': 'dj_core',
        'DJCORE_APP_CONF': '',
        'DJCORE_DEBUG': False,
    }

    def __init__(self, *args, **kwargs):
        self._env = None
        self.settings = self.get_settings()
        super(BaseConfig, self).__init__(*args, **kwargs)

    @property
    def env(self):
        if self._env is None:
            self._env = Env(**self.types)
        return self._env

    @property
    def app_name(self):
        return self.env('DJCORE_APP_NAME')

    @property
    def app_conf_str(self):
        val = self.env('DJCORE_APP_CONF')
        if val == '':
            val = '{}.config.Config'.format(self.app_name)
        return val.replace('-', '_')

    @property
    def app_conf(self):
        module, conf = self.app_conf_str.rsplit('.', 1)
        return getattr(import_module(module), conf)

    @property
    def debug(self):
        return Env().str('DJCORE_DEBUG', False)

    @property
    def types(self):
        return {k: (type(v), v) for k, v in self.get_defaults().items()}

    def get_defaults(self):  # pylint: disable=no-self-use
        return self.defaults

    def get_settings(self):  # pylint: disable=no-self-use
        return AttrDict({'DEBUG': self.env('DJCORE_DEBUG')})


class Config(BaseConfig):
    defaults_dict = AttrDict({
        'simple': {
            'DJCORE_ALLOWED_HOSTS': ['localhost'],
            'DJCORE_ANONYMOUS_USER_ID': -1,
            'DJCORE_AUTHENTICATION_BACKENDS': ['django.contrib.auth.backends.ModelBackend'],
            'DJCORE_AUTH_USER_MODEL': 'minimal_user.User',
            'DJCORE_AWS_ACCESS_KEY_ID': '',
            'DJCORE_AWS_S3_ENDPOINT_URL': '',
            'DJCORE_AWS_S3_REGION_NAME': '',
            'DJCORE_AWS_SECRET_ACCESS_KEY': '',
            'DJCORE_AWS_STORAGE_BUCKET_NAME': '',
            'DJCORE_CELERY_BROKER_TRANSPORT_OPTIONS': {'visibility_timeout': 3600},  # 1 hour.
            'DJCORE_CELERY_BROKER_URL': 'redis://',
            'DJCORE_CORS_ORIGIN_ALLOW_ALL': False,
            'DJCORE_CSRF_COOKIE_PATH': '/backend/',
            'DJCORE_CSRF_COOKIE_SECURE': True,
            'DJCORE_DEFAULT_FILE_STORAGE': 'dj_core.storage.MediaS3',
            'DJCORE_EMAIL_BACKEND': 'anymail.backends.mailgun.MailgunBackend',
            'DJCORE_INTERNAL_IPS': ['127.0.0.1'],
            'DJCORE_LANGUAGE_CODE': 'en-AU',
            'DJCORE_LOGIN_URL': '/backend/login/',
            'DJCORE_MEDIA_URL': '/assets/media/',
            'DJCORE_ROOT_URLCONF': 'dj_core.urls',
            'DJCORE_SECRET_KEY': '',
            'DJCORE_SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
            'DJCORE_SESSION_COOKIE_PATH': '/backend/',
            'DJCORE_SESSION_COOKIE_SECURE': True,
            'DJCORE_SITE_ID': 1,
            'DJCORE_STATICFILES_STORAGE': 'dj_core.storage.StaticS3',
            'DJCORE_STATIC_URL': '/assets/static/',
            'DJCORE_TIME_ZONE': 'UTC',
            'DJCORE_USE_I18N': True,
            'DJCORE_USE_L10N': True,
            'DJCORE_USE_TZ': True,
            'DJCORE_VAR_ROOT': '/var',
            'DJCORE_WSGI_APPLICATION': 'dj_core.wsgi.application',
        },
        'djcore': {
            'DJCORE_ADMIN_ENABLED': True,
            'DJCORE_ADMIN_USER': {},
            'DJCORE_FRONTEND_URL': 'https://localhost',
            'DJCORE_SITE_URL': 'https://localhost',
            'DJCORE_USE_DJDT': False,
            'DJCORE_WHITELIST_SITE_URL': True,
        },
        'complex': {
            'DJCORE_ADMINS': [],
            'DJCORE_MANAGERS': [],
            'DJCORE_SITE_NAME': '',
        },
        'proxied': AttrDict([  # order is important
            ('DJCORE_CELERY_APP_NAME', ('', lambda conf: conf.DJCORE.APP_NAME)),
            ('DJCORE_CELERY_RESULT_BACKEND', ('', lambda conf: conf.CELERY_BROKER_URL)),
            ('DJCORE_CORS_ORIGIN_WHITELIST', ([], lambda conf: conf.ALLOWED_HOSTS)),
            ('DJCORE_CSRF_TRUSTED_ORIGINS', ([], lambda conf: conf.CORS_ORIGIN_WHITELIST)),
            ('DJCORE_CACHE_ROOT', ('', lambda conf: path.join(conf.VAR_ROOT, 'cache'))),
            ('DJCORE_LOG_ROOT', ('', lambda conf: path.join(conf.VAR_ROOT, 'log'))),
            ('DJCORE_DOCUMENT_ROOT', ('', lambda conf: path.join(conf.VAR_ROOT, 'www'))),
            ('DJCORE_STATIC_ROOT', ('', lambda conf: path.join(conf.DOCUMENT_ROOT, 'static'))),
            ('DJCORE_MEDIA_ROOT', ('', lambda conf: path.join(conf.DOCUMENT_ROOT, 'media'))),
        ]),
        'dev': {
            'DJCORE_ADMIN_USER': {'email': 'test@example.com', 'password': 'password'},
            'DJCORE_ALLOWED_HOSTS': ['*'],
            'DJCORE_AWS_ACCESS_KEY_ID': 'djangos3',
            'DJCORE_AWS_S3_ENDPOINT_URL': 'http://minio:9000',
            'DJCORE_AWS_SECRET_ACCESS_KEY': 'djangos3',
            'DJCORE_AWS_STORAGE_BUCKET_NAME': 'django',
            'DJCORE_CELERY_BROKER_URL': 'redis://redis',
            'DJCORE_CELERY_RESULT_BACKEND': 'redis://redis',
            'DJCORE_CORS_ORIGIN_ALLOW_ALL': True,
            'DJCORE_CSRF_COOKIE_SECURE': False,
            'DJCORE_DATABASE_URL': 'postgis://django:django@db:5432/django',
            'DJCORE_EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
            'DJCORE_SESSION_COOKIE_SECURE': False,
            'DJCORE_TEMPLATE_DEBUG': True,
            'DJCORE_USE_DJDT': True,
        },
    })

    @property
    def djdt_enabled(self):
        return self.debug and self.env('DJCORE_USE_DJDT')

    @property
    def site_url(self):
        return six.moves.urllib.parse.urlparse(self.env('DJCORE_SITE_URL'))  # pylint: disable=no-member

    def get_env(self, key, default):
        val = self.env.get_value(key, type(default), default)
        return default if val in [[], None, ''] else val

    def get_env_vals(self, keys):
        return AttrDict({key[7:]: self.env(key) for key in keys})  # remove DJCORE_

    def get_defaults(self):
        defaults = super(Config, self).get_defaults()
        defaults.update(self.defaults_dict.simple)
        defaults.update(self.defaults_dict.djcore)
        defaults.update(self.defaults_dict.complex)
        defaults.update({k: v[0] for k, v in self.defaults_dict.proxied.items()})
        if self.debug:
            defaults.update(self.defaults_dict.dev)
        return defaults

    def get_settings(self):
        settings = super(Config, self).get_settings()
        settings.update(self.get_core_settings())
        settings.DJCORE = self.get_djcore_settings(settings)
        self.apply_proxied_settings(settings)
        settings.DATABASES = self.get_databases(settings)
        settings.INSTALLED_APPS = self.get_installed_apps(settings)
        settings.MIDDLEWARE = self.get_middleware(settings)
        settings.TEMPLATES = self.get_templates(settings)
        settings.update(self.get_email_settings(settings))
        return settings

    def get_core_settings(self):
        conf = self.get_env_vals(self.defaults_dict.simple)
        if self.djdt_enabled:
            conf.DEBUG_TOOLBAR_CONFIG = {
                'SHOW_COLLAPSED': True,
                'SHOW_TOOLBAR_CALLBACK': lambda request: True
            }
        return conf

    def apply_proxied_settings(self, conf):
        conf.ALLOWED_HOSTS = conf.ALLOWED_HOSTS + conf.INTERNAL_IPS
        for key, (_, call) in self.defaults_dict.proxied.items():
            conf[key[7:]] = call(conf)
        if self.env('DJCORE_WHITELIST_SITE_URL'):
            conf.ALLOWED_HOSTS += [self.site_url.netloc]
            conf.CSRF_TRUSTED_ORIGINS += [
                x for x in conf.ALLOWED_HOSTS
                if x not in conf.CSRF_TRUSTED_ORIGINS]
            conf.CORS_ORIGIN_WHITELIST += [
                x for x in conf.CSRF_TRUSTED_ORIGINS
                if x not in conf.CORS_ORIGIN_WHITELIST]

    def get_djcore_settings(self, settings):  # pylint: disable=unused-argument
        conf = self.get_env_vals(self.defaults_dict.djcore)
        conf.update({
            'SITE_DOMAIN': self.site_url.netloc,
            'APP_NAME': self.env('DJCORE_APP_NAME'),
            'APP_CONF': self.env('DJCORE_APP_CONF'),
        })
        conf.SITE_NAME = self.get_env('DJCORE_SITE_NAME', conf.APP_NAME)
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
            'corsheaders',
            'anymail',
            'django_extensions',
            'storages',
        ] if _can_import(x)] + ([
            'debug_toolbar',
            'debug_toolbar_line_profiler',
        ] if self.djdt_enabled else [])

    def get_middleware(self, settings):  # pylint: disable=unused-argument
        return ([
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        ] if self.djdt_enabled else []) + [
            'django.contrib.sessions.middleware.SessionMiddleware',
        ] + ([
            'corsheaders.middleware.CorsMiddleware'
        ] if _can_import('corsheaders') else []) + [
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
                'MAILGUN_API_KEY': self.env.str('DJCORE_MAILGUN_API_KEY'),
                'MAILGUN_SENDER_DOMAIN': self.env.str(
                    'DJCORE_MAILGUN_SENDER_DOMAIN',
                    'mailgun.%s' % self.site_url.hostname),
            }
        return conf
