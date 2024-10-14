from .base import *


DEBUG = True
# ALLOWED_HOSTS = ['api.chalkmates.com', 'graph.chalkmates.com', 'playground.chalkmates.com',
#                  'api.yucampus.com', 'graph.yucampus.com', 'playground.yucampus.com']
ALLOWED_HOSTS=['*']

# 3rd party apps
THIRD_PARTY_APPS = ['corsheaders']
INSTALLED_APPS += THIRD_PARTY_APPS

# added middlewares
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', *MIDDLEWARE]

# cors
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https?:\/\/.*\.?chalkmates\.com\/?.*',
    r'^https?:\/\/.*\.?yucampus\.com\/?.*',
]
ACCESS_CONTROL_ALLOW_HEADERS = True
CORS_ALLOW_HEADERS = ['*']

# media
MEDIA_URL = '/media/'

# media & static
AWS_ACCESS_KEY_ID = ENV.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = ENV.str('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = ENV.str('AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_S3_REGION_NAME = ENV.str('AWS_S3_REGION_NAME')
AWS_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
