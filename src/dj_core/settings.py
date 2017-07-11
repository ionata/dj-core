from __future__ import absolute_import, print_function, unicode_literals

from .config import BaseConfig


globals().update(BaseConfig().app_conf().settings)  # pylint: disable=not-callable
