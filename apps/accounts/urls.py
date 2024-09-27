from django.conf.urls import url
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import *
app_name = 'accounts'

router = DefaultRouter()
router.register('users', UserViewSet)


urlpatterns = [
   url('login/$', Login.as_view(), name='user_login'),
   path('', include(router.urls)),
]