#!/usr/bin/env python26

import site
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
# Used to translate every path in settings.py to an absolute path.
path = lambda *a: os.path.join(ROOT, *a)

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

#site.addsitedir(path('apps'))


if __name__ == "__main__":
    execute_manager(settings)
