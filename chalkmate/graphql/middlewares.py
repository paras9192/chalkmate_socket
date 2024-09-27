'''
These middlewares are exclusively for graphql.
They Run from right-to-left fashion
'''

from re import sub
from django.forms import ValidationError
from graphql import MiddlewareManager
from rest_framework.authtoken.models import Token

def inject_user_obj_middleware(resolver, obj, info, **kwargs):
    iuom = info.context.get('iuom', False)
    if iuom:
        return resolver(obj, info, **kwargs)
    else:
        info.context['iuom'] = True
    request = info.context['request']
    header_token = request.META.get('HTTP_AUTHORIZATION', None)
    if header_token is not None:
        try:
            token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
            token_obj = Token.objects.get(key=token)
            info.context['user'] = token_obj.user
            info.context['user_is_authenticated'] = True
        except Token.DoesNotExist:
            info.context['user'] = None
            info.context['user_is_authenticated'] = False
    return resolver(obj, info, **kwargs)

def auth_middleware(resolver, obj, info, **kwargs):
    am = info.context.get('am', False)
    if am:
        return resolver(obj, info, **kwargs)
    else:
        info.context['am'] = True
    user = info.context.get('user', None)
    is_auth = info.context.get('user_is_authenticated', None)
    if user is not None and is_auth:
        return resolver(obj, info, **kwargs)
    raise ValidationError("Unauthenticated request")

middleware = MiddlewareManager(auth_middleware, inject_user_obj_middleware)