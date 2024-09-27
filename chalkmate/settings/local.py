from .base import *


DEBUG = True
ALLOWED_HOSTS = ['*']


# 3rd party apps
THIRD_PARTY_APPS = []
INSTALLED_APPS += THIRD_PARTY_APPS

# added middlewares
# MIDDLEWARE = [*MIDDLEWARE, 'apps.translations.middleware.CustomCacheMiddleware']

# cors
CORS_ALLOW_ALL_ORIGINS = True
ACCESS_CONTROL_ALLOW_HEADERS=True
CORS_ALLOW_HEADERS=['*']
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'.*'
]

# media
MEDIA_URL = '/media/'

