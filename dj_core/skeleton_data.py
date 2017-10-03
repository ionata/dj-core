from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


def get_admin(default_defaults=None):
    admin = settings.DJCORE.ADMIN_USER
    model = get_user_model()
    if model is None:
        raise ImportError("Cannot import the specified User model")
    username = model.USERNAME_FIELD
    defaults = {x: True for x in ['is_staff', 'is_superuser', 'is_active']}
    if default_defaults is not None:
        defaults.update(default_defaults)
    defaults.update({
        k: v for k, v in admin.items() if k not in [username, 'password']})
    try:
        values = {username: admin[username], 'defaults': defaults}
        user, new = model.objects.get_or_create(**values)
    except IntegrityError:
        raise AttributeError("Admin user not found or able to be created.")
    if new:
        user.set_password(admin['password'])
        user.save()
    return user


def get_site():
    from django.contrib.sites.models import Site
    defaults = {
        'name': settings.DJCORE.SITE_NAME,
        'domain': settings.DJCORE.SITE_DOMAIN,
    }
    return Site.objects.update_or_create(pk=settings.SITE_ID, defaults=defaults)[0]


def setup():
    get_admin()
    get_site()
