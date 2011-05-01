from settings import *


DEBUG = True
COMPRESS = False

BASE_URL = ''

BASE_URL = BASE_URL.rstrip('/')
MEDIA_URL = '%s/media/' % BASE_URL
ADMIN_MEDIA_PREFIX = '%s/admin-media/' % BASE_URL
LOGIN_REDIRECT_URL = '%s/machines/' % BASE_URL
LOGIN_URL = '%s/accounts/login/' % BASE_URL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'littlesis',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '',
        'PORT': '',
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    }
}

# If you're not running on SSL, you'll want this to be False.
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = None

CACHE_BACKEND = 'dummy://'
