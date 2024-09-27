from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url, include, static
from django.conf import settings
from apps.accounts.urls import router as accounts_router
# from apps.zoom.urls import router as zoom_router
# from apps.gradebook.urls import router as gradebook_router
# from apps.dashboard.urls import router as dashboard_router
# from apps.classes.urls import router as classes_router
# from apps.assignments.urls import router as assignments_router
# from apps.groups.urls import router as groups_router
# from apps.payment.urls import router as payment_router
# from apps.liveChat.urls import router as chatrouter
from chalkmate.graphql.errors import custom_error_format
# from apps.enterpriseDashboard.urls import router as enterprise_router
from .views import welcome
from rest_framework.routers import DefaultRouter
# from apps.userProfile.views import SubscribedUserDataViewSet
from ariadne_django.views import GraphQLView
from graphql_playground.views import GraphQLPlaygroundView
# from .graphql.schema import schema
from .graphql.middlewares import middleware
from django.views.generic import TemplateView

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL
STATIC_URL = settings.STATIC_URL

router = DefaultRouter()
# router.register(r"subscribe", SubscribedUserDataViewSet, "subscribe")
# router.registry.extend(accounts_router.registry)
# router.registry.extend(zoom_router.registry)
# router.registry.extend(dashboard_router.registry)
# router.registry.extend(classes_router.registry)
# router.registry.extend(groups_router.registry)
# router.registry.extend(payment_router.registry)
# router.registry.extend(assignments_router.registry)
# router.registry.extend(gradebook_router.registry)
# router.registry.extend(chatrouter.registry)
# router.registry.extend(enterprise_router.registry)


# PLAYGROUND_OPTIONS = {
#     "settings": {
#         "request.credentials": "include",
#     }
# }

urlpatterns = [
    path('admin/', admin.site.urls),
    path('direct-html/', TemplateView.as_view(template_name='pay.html'), name='direct_html'),
    # path('graphql/', GraphQLView.as_view(schema=schema, middleware=middleware, error_formatter=custom_error_format, template_name='error/index.html'), name='graphql'),
    path('playground/', GraphQLPlaygroundView.as_view(endpoint="playground")),
    re_path(r'^api/v1/', include(router.urls)),
    # re_path(r'^api/v1/', include('apps.accounts.urls', namespace='accounts')),
    path('api/v1/', include('apps.accounts.urls', namespace='accounts')),
    # re_path(r'^api/v1/', include('apps.classes.urls', namespace='classes')),
    # re_path(r'^api/v1/', include('apps.groups.urls', namespace='groups')),
    # re_path(r'^api/v1/', include('apps.payment.urls')),
    # re_path(r'^api/v1/', include('apps.dashboard.urls', namespace='dashboard')),
    # re_path(r'^api/v1/', include('apps.userProfile.urls')),
    # re_path(r'^api/v1/', include('apps.translations.urls')),
    # re_path(r'^api/v1/', include('apps.liveChat.urls')),
    # re_path(r'^api/v1/', include('apps.enterpriseDashboard.urls', namespace='enterpriseDashboard')),
    # re_path(r'^hooks', include('hooks.urls')),
    url('^api/v1/welcome', welcome),
]

urlpatterns += static.static(MEDIA_URL, document_root=MEDIA_ROOT)

admin.site.site_header = 'yucampus Admin'
admin.site.site_title = 'yucampus Admin'
admin.site.index_title = "Welcome to yucampus"
