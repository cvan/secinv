#!/usr/bin/env python26

import os
import site
import sys
import warnings


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


prev_sys_path = list(sys.path)


site.addsitedir(path('apps'))

# Move the new items to the front of sys.path. (via virtualenv)
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

from django.core.management import execute_manager, setup_environ

if not settings.DEBUG:
    warnings.simplefilter('ignore')

setup_environ(settings)


if __name__ == "__main__":
    execute_manager(settings)
