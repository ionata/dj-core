from __future__ import absolute_import, print_function, unicode_literals

from django.core.management.base import BaseCommand
from dj_core.utils import get_app_submodules


class Command(BaseCommand):
    def handle(self, *args, **options):
        for app_name, module in get_app_submodules('skeleton_data'):
            print('Running setup for {}'.format(app_name))
            module.setup()
