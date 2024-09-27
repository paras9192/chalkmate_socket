"""
WSGI config for chalkmate project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from chalkmate.settings.base import ENV

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f"chalkmate.settings.{ENV.str('ENV_TYPE')}")

application = get_wsgi_application()
