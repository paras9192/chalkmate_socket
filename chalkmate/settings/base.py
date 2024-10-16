""" 
@author: Anmol Goel
@date: 13-Aug-2021
Django version used : 3.0
"""

import logging.config
from pathlib import Path
import environ
import os
from chalkmate.logger import LOGGING
from django.apps import AppConfig
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = (
    environ.Path(__file__) - 3
)
import pymysql

# Initialise environment variables
ENV = environ.Env()
pymysql.install_as_MySQLdb()
environ.Env.read_env(os.path.join(ENV_DIR, '.env'))


AppConfig.default = False

SECRET_KEY = ENV.str('SECRET_KEY')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_crontab',
    'ariadne_django',
    'graphql_playground',
    'profanity',
    'apps.accounts',
    'apps.chatapp'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'apps.translations.middleware.CustomCacheMiddleware',

]

ROOT_URLCONF = 'chalkmate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chalkmate.wsgi.application'



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# base for static and media
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    BASE_DIR / "static/assets",
]
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# REST FRAMEWORK SETTINGS
""" Defining custom user auth """
AUTH_USER_MODEL ='accounts.User'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES' : (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        ),
    'EXCEPTION_HANDLER': 'chalkmate.exception.my_exception_handler',
}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# to disable the check
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# pagination defalut limit 
DEFAULT_LIMIT = ENV.int('DEFAULT_LIMIT')

# zoom settings
ZOOM_JWT_API_KEY = ENV.str('ZOOM_JWT_API_KEY')
ZOOM_JWT_API_SECRET = ENV.str('ZOOM_JWT_API_SECRET')
ZOOM_WEBHOOK_SECRET_TOKEN = ENV.str('ZOOM_WEBHOOK_SECRET_TOKEN')

#mailer settings
EMAIL_USE_TLS = ENV.str('EMAIL_USE_TLS')
EMAIL_PORT = ENV.str('EMAIL_PORT')
EMAIL_BACKEND = ENV.str('EMAIL_BACKEND')
EMAIL_HOST = ENV.str('EMAIL_HOST')
EMAIL_HOST_USER = ENV.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = ENV.str('EMAIL_HOST_PASSWORD')

#pusher settings
PUSHER_APP_ID = ENV.str('PUSHER_APP_ID')
PUSHER_KEY = ENV.str('PUSHER_KEY')
PUSHER_SECRET = ENV.str('PUSHER_SECRET')
CLUSTER = ENV.str('CLUSTER')

# frontend url for mailers
FRONTEND_RESET_PASSWORD_BASE_URL = ENV.str("FRONTEND_RESET_PASSWORD_BASE_URL")

#razorpay 
RAZORPAY_KEY_ID = ENV.str("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = ENV.str("RAZORPAY_KEY_SECRET")

# database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': ENV.str('DATABASE_NAME'),
        'USER': ENV.str('DATABASE_USER'),
        'PASSWORD': ENV.str('DATABASE_PASS'),
        'HOST': ENV.str('DATABASE_HOST'),
        'PORT': ENV.str('DATABASE_PORT'),
        "OPTIONS": {"charset": "utf8mb4"}, # for emojis
    }
}

# crons
CRONJOBS = [
    ('30 5 * * *', 'apps.payment.cron.ServiceSubcription' ),
]

STUDENT_TYPE = ["STUDENT"]
TEACHER_TYPE = ["TRAINER","FACULTY","SCHOOL","PROFESSIONALL","ENTERPRISE"]


# google translate api cred
GOOGLE_TRANSLATION_API_KEY = ENV.str('GOOGLE_TRANSLATION_API_KEY')
GOOGLE_TRANSLATION_BASE_URL = ENV.str('GOOGLE_TRANSLATION_BASE_URL')
USE_TRANSLATE = ENV.str('USE_TRANSLATE')

#server base url
BACKEND_SERVER_URL = ENV.str('BACKEND_SERVER_URL')

# cache timeout
CM_CACHE_MIDDLEWARE_SECONDS = ENV.int('CACHE_TIMEOUT')

# caches database
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": ENV.str('CACHE_SERVER'),
        'KEY_PREFIX': 'chalkmates',
        "OPTIONS": {
            "PASSWORD": ENV.str('CACHE_PASSWORD'),
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}

# logging
LOGGING_CONFIG = None
logging.config.dictConfig(LOGGING)
LOGGEER = logging.getLogger('chalkmate') 

CUSTOM_ERROR_MESSAGE = "Something went wrong. Try again after sometime"


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }


