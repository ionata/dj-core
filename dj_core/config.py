# pylint: disable=not-callable
from __future__ import absolute_import, print_function, unicode_literals

from importlib import import_module
from operator import attrgetter as ga
from os import path

# pylint: disable=no-name-in-module,import-error
from django.utils.six.moves.urllib.parse import urlparse

from dj_core.utils import (
    AttrDict, DjCoreEnv as Env, EmailList, Undefined, import_from_string)


UNDEFINED = Undefined()


def _fmt(attr, template):
    return lambda c: template.format(ga(attr)(c))


def _can_import(app_name):
    try:
        import_module(app_name)
    except ImportError:
        return False
    return True


def _installed(app_name, if_true, if_false):
    return lambda c: if_true if app_name in c.INSTALLED_APPS else if_false


def _docpath(conf_key, folder):
    return lambda c: path.join(getattr(c, conf_key), folder)


class DefaultProxy(object):
    def __init__(self, typ, func=None):
        self.typ = typ if isinstance(typ, type) else type(typ)
        self.func = func


def get_types(env_dict):
    return {k: (getattr(v, 'typ', type(v)), v) for k, v in env_dict.items()}


class BaseConfig(object):
    base_defaults = AttrDict([
        ('APP_NAME', 'dj_core'),
        ('APP_CONF', ''),
        ('DEBUG', False),
    ])
    defaults = base_defaults.copy()
    defaults_dev = AttrDict()

    def __init__(self, conf_name=None, *args, **kwargs):
        super(BaseConfig, self).__init__(*args, **kwargs)
        self._env = None
        self._conf = None
        self._defaults = None
        env = Env(**get_types(self.base_defaults))
        self.debug = env('DEBUG')
        if conf_name is None:
            self.app_name = env('APP_NAME')
            conf_name = env('APP_CONF') or '%s.config.Config' % self.app_name
        else:
            self.app_name = conf_name.split('.')[0]
        self.app_conf = import_from_string(conf_name)

    def get_defaults(self):
        if self._defaults is None:
            self._defaults = self.defaults.copy()
            if self.debug:
                self._defaults.update(self.defaults_dev.copy())
        return self._defaults

    def env(self, key, default, conf):
        if self._env is None:
            self._env = Env(**get_types(self.get_defaults()))
        val = self._env(key, default=UNDEFINED)
        if val is UNDEFINED:
            val = default
        if isinstance(val, DefaultProxy):
            func = val.func
            if isinstance(val.func, str):
                func = getattr(self, val.func, val.func)
            if func is None:
                raise ValueError('No value for %s' % self._env.prefix(key))
            val = func(conf)
        return val

    @staticmethod
    def _set(conf, key, val):
        parent = conf
        if '__' in key:
            parts = key.split('__')
            for part in parts[:-1]:
                if part not in parent:
                    parent[part] = AttrDict()
                parent = parent[part]
            key = parts[-1]
        parent[key] = val

    def get_settings(self):
        conf = AttrDict()
        for key, default in self.get_defaults().items():
            self._set(conf, key.strip('_'), self.env(key, default, conf))
        return conf

    @property
    def settings(self):
        if self._conf is None:
            self._conf = self.get_settings()
        return self._conf


class Config(BaseConfig):
    defaults = BaseConfig.defaults.copy()
    defaults.update([
        # dj_core internal settings
        ('DJCORE__APP_NAME', DefaultProxy('', ga('APP_NAME'))),
        ('DJCORE__APP_CONF', DefaultProxy('', ga('APP_CONF'))),
        ('DJCORE__ADMIN_ENABLED', True),
        ('DJCORE__ADMIN_USER', {}),
        ('DJCORE__SITE_URL', 'https://localhost'),
        ('DJCORE__FRONTEND_URL', DefaultProxy('', ga('DJCORE.SITE_URL'))),
        ('DJCORE__WHITELIST_SITE_URL', True),
        ('DJCORE__URL', DefaultProxy('', lambda c: (urlparse(c.DJCORE.SITE_URL)))),
        ('DJCORE__SITE_NAME', DefaultProxy('', ga('DJCORE.APP_NAME'))),
        ('DJCORE__SITE_DOMAIN', DefaultProxy('', lambda c: c.DJCORE.URL.netloc)),
        ('DJCORE__USE_DJDT', False),
        ('DJCORE__DJDT_ENABLED', DefaultProxy(False, lambda c: (
            c.DEBUG and _can_import('debug_toolbar') and c.DJCORE.USE_DJDT))),

        # core settings (utilise Config methods)
        ('INSTALLED_APPS_REQUIRED', [
            'dj_core',
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.sites',
        ]),
        ('INSTALLED_APPS_OPTIONAL', [
            'minimal_user',
            'corsheaders',
            'anymail',
            'django_extensions',
            'storages',
        ]),
        ('DATABASE_URL', ''),
        ('INSTALLED_APPS', DefaultProxy([], 'get_installed_apps')),
        ('DATABASES', DefaultProxy({}, 'get_databases')),
        ('MIDDLEWARE', DefaultProxy({}, 'get_middleware')),
        ('TEMPLATES', DefaultProxy({}, 'get_templates')),
        ('ALLOWED_HOSTS', DefaultProxy([], 'get_allowed_hosts')),

        # simple settings (in case overrides want to proxy core settings)
        ('ADMINS', EmailList()),
        ('ANONYMOUS_USER_ID', -1),
        ('AUTHENTICATION_BACKENDS', ['django.contrib.auth.backends.ModelBackend']),
        ('AWS_ACCESS_KEY_ID', ''),
        ('AWS_S3_ENDPOINT_URL', ''),
        ('AWS_S3_REGION_NAME', ''),
        ('AWS_S3_CUSTOM_DOMAIN', ''),
        ('AWS_SECRET_ACCESS_KEY', ''),
        ('AWS_STORAGE_BUCKET_NAME', ''),
        ('CELERY_BROKER_TRANSPORT_OPTIONS', {'visibility_timeout': 3600}),  # 1 hour.
        ('CELERY_BROKER_URL', 'redis://'),
        ('CORS_ORIGIN_ALLOW_ALL', False),
        ('CSRF_COOKIE_PATH', '/backend/'),
        ('CSRF_COOKIE_SECURE', True),
        ('INTERNAL_IPS', ['127.0.0.1']),
        ('LANGUAGE_CODE', 'en-AU'),
        ('LOGIN_URL', '/backend/login/'),
        ('MAILGUN_API_KEY', ''),
        ('MANAGERS', EmailList()),
        ('MEDIA_URL', '/assets/media/'),
        ('ROOT_URLCONF', 'dj_core.urls'),
        ('SECRET_KEY', ''),
        ('SECURE_PROXY_SSL_HEADER', ('HTTP_X_FORWARDED_PROTO', 'https')),
        ('SESSION_COOKIE_PATH', '/backend/'),
        ('SESSION_COOKIE_SECURE', True),
        ('SITE_ID', 1),
        ('STATIC_URL', '/assets/static/'),
        ('TIME_ZONE', 'UTC'),
        ('USE_I18N', True),
        ('USE_L10N', True),
        ('USE_TZ', True),
        ('VAR_ROOT', '/var'),
        ('WSGI_APPLICATION', 'dj_core.wsgi.application'),

        # proxied settings
        ('CELERY_APP_NAME', DefaultProxy('', ga('DJCORE.APP_NAME'))),
        ('CELERY_RESULT_BACKEND', DefaultProxy('', ga('CELERY_BROKER_URL'))),
        ('CORS_ORIGIN_WHITELIST', DefaultProxy([], ga('ALLOWED_HOSTS'))),
        ('CSRF_TRUSTED_ORIGINS', DefaultProxy([], ga('CORS_ORIGIN_WHITELIST'))),
        ('CACHE_ROOT', DefaultProxy('', _docpath('VAR_ROOT', 'cache'))),
        ('LOG_ROOT', DefaultProxy('', _docpath('VAR_ROOT', 'log'))),
        ('DOCUMENT_ROOT', DefaultProxy('', _docpath('VAR_ROOT', 'www'))),
        ('STATIC_ROOT', DefaultProxy('', _docpath('DOCUMENT_ROOT', 'static'))),
        ('MEDIA_ROOT', DefaultProxy('', _docpath('DOCUMENT_ROOT', 'media'))),
        ('EMAIL_SUBJECT_PREFIX', DefaultProxy('', _fmt('DJCORE.APP_NAME', '[Django - {}] '))),
        ('DEFAULT_FROM_EMAIL', DefaultProxy('', _fmt('DJCORE.URL.hostname', 'no-reply@{}'))),
        ('SERVER_EMAIL', DefaultProxy('', _fmt('DJCORE.URL.hostname', 'no-reply+system@{}'))),
        ('MAILGUN_SENDER_DOMAIN', DefaultProxy('', _fmt('DJCORE.URL.hostname', 'mailgun.{}'))),
        ('AUTH_USER_MODEL', DefaultProxy('', _installed(
            'minimal_user', 'minimal_user.User', 'auth.User'))),
        ('EMAIL_BACKEND', DefaultProxy('', _installed(
            'anymail', 'anymail.backends.mailgun.EmailBackend',
            'django.core.mail.backends.smtp.EmailBackend'
        ))),
        ('DEFAULT_FILE_STORAGE', DefaultProxy('', _installed(
            'storages', 'dj_core.storage.MediaS3',
            'django.core.files.storage.FileSystemStorage'))),
        ('STATICFILES_STORAGE', DefaultProxy('', _installed(
            'storages', 'dj_core.storage.StaticS3',
            'django.contrib.staticfiles.storage.StaticFilesStorage'))),
    ])
    defaults_dev = AttrDict([
        ('ALLOWED_HOSTS', ['*']),
        ('AWS_ACCESS_KEY_ID', 'djangos3'),
        ('AWS_S3_ENDPOINT_URL', 'http://minio:9000'),
        ('AWS_SECRET_ACCESS_KEY', 'djangos3'),
        ('AWS_STORAGE_BUCKET_NAME', 'django'),
        ('CELERY_BROKER_URL', 'redis://redis'),
        ('CELERY_RESULT_BACKEND', 'redis://redis'),
        ('CORS_ORIGIN_ALLOW_ALL', True),
        ('CSRF_COOKIE_SECURE', False),
        ('DATABASE_URL', 'postgis://django:django@db:5432/django'),
        ('DEBUG_TOOLBAR_CONFIG', {'SHOW_COLLAPSED': True, 'SHOW_TOOLBAR_CALLBACK': lambda request: True}),
        ('DJCORE__ADMIN_USER', {'email': 'test@example.com', 'password': 'password'}),
        ('DJCORE__USE_DJDT', True),
        ('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'),
        ('SECRET_KEY', 'super_secret_secret_key'),
        ('SESSION_COOKIE_SECURE', False),
    ])

    def get_allowed_hosts(self, conf):  # pylint: disable=no-self-use
        return ['localhost'] + (
            [conf.DJCORE.URL.netloc]
            if conf.DJCORE.WHITELIST_SITE_URL else [])

    def get_databases(self, conf):  # pylint: disable=unused-argument,no-self-use
        return {'default': Env.db_url_config(conf.DATABASE_URL)}

    def get_installed_apps(self, conf):  # pylint: disable=no-self-use
        return (lambda apps: (
            [] if conf.DJCORE.APP_NAME in apps else [conf.DJCORE.APP_NAME]
        ) + apps)(
            conf.INSTALLED_APPS_REQUIRED.copy() + [
                x for x in conf.INSTALLED_APPS_OPTIONAL if _can_import(x)
            ] + (['debug_toolbar'] if conf.DJCORE.DJDT_ENABLED else []))

    def get_middleware(self, conf):  # pylint: disable=no-self-use
        return (
            _installed(
                'debug_toolbar',
                ['debug_toolbar.middleware.DebugToolbarMiddleware'], [])(conf)
        ) + ['django.contrib.sessions.middleware.SessionMiddleware'] + (
            _installed(
                'corsheaders',
                ['corsheaders.middleware.CorsMiddleware'], [])(conf)
        ) + [
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'django.middleware.security.SecurityMiddleware',
        ]

    def get_templates(self, conf):  # pylint: disable=no-self-use,unused-argument
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


def get_conf(conf_name=None):
    return BaseConfig(conf_name).app_conf()
