from __future__ import absolute_import, print_function, unicode_literals

from dj_core.config import get_conf


globals().update(get_conf().settings)  # pylint: disable=not-callable
