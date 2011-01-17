#!/usr/bin/env python26

import os
import site
import sys

from django.core.management import execute_manager


ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

try:
    import settings_local as settings
except ImportError:
    try:
        import settings
    except ImportError:
        import sys
        sys.stderr.write(
            "Error: Tried importing 'settings_local.py' and 'settings.py' "
            "but neither could be found (or they're throwing an ImportError). "
            "Please come back and try again later.")
        raise

site.addsitedir(path('apps'))

if __name__ == "__main__":
    execute_manager(settings)
