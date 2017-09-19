from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
try:
    from storages.backends import s3boto3
except ImportError:
    pass
else:
    class StaticS3(s3boto3.S3Boto3Storage):  # pylint: disable=abstract-method
        location = settings.STATIC_URL

    class MediaS3(s3boto3.S3Boto3Storage):  # pylint: disable=abstract-method
        location = settings.MEDIA_URL
