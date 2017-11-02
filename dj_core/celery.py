"""Bootstrap celery with Django's config"""
from __future__ import absolute_import, print_function, unicode_literals

from celery import Celery
from django.conf import settings


app = Celery(settings.CELERY_APP_NAME)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
