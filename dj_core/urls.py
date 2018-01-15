from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.conf.urls import include, url

from .utils import get_app_submodules


def _admin_urls():
    if not settings.DJCORE.ADMIN_ENABLED:
        return []
    from django.contrib import admin
    return [url(r'^backend/django-admin/', admin.site.urls)]


def _djdt_urls():
    if not settings.DJCORE.DJDT_ENABLED:
        return []
    import debug_toolbar
    return [url(r'^backend/__debug__/', include(debug_toolbar.urls))]


def _static_urls():
    if not settings.DEBUG:
        return []
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    _static = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    return staticfiles_urlpatterns() + _static


def get_urls():
    urls = []
    # Add urls from apps in urlpatterns from a 'routes' package
    for app_name, module in get_app_submodules('routes'):
        if app_name != __package__ and hasattr(module, 'urlpatterns'):
            urls += module.urlpatterns
    return _admin_urls() + _djdt_urls() + _static_urls() + urls


urlpatterns = get_urls()
