from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from .utils import custom_success_response, update_object_response

class ModelViewSet(viewsets.ModelViewSet):
    _instance = None

    def perform_create(self, serializer, **kwargs):
        self._instance = serializer.save(**kwargs)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return custom_success_response(serializer.data)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return custom_success_response(self.get_serializer(self._instance).data, status=status.HTTP_201_CREATED, headers=headers)
    def perform_update(self, serializer):
        self._instance = serializer.save()
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return update_object_response(message="success, object updated")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return custom_success_response(serializer.data)
    def perform_destroy(self, instance):
        instance.delete()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return update_object_response(message="success, object deleted", status=status.HTTP_204_NO_CONTENT)
        
class CustomPaginationViewset (LimitOffsetPagination):
    default_limit = settings.DEFAULT_LIMIT

    def get_limit(self, request):
        """
        Override get_limit to allow dynamic pagination limit.
        """
        limit = super().get_limit(request)
        # Retrieve count from query parameters
        df_count = request.query_params.get('dynamic_limit')
        # If count is provided, use it as limit, else use default
        if df_count is not None:
            return int(df_count)
        return limit
    def get_paginated_response(self, data):
        kwargs = {
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link()
        }
        return custom_success_response(data, message='success', status=status.HTTP_200_OK, **kwargs)

class EnterpriseCustomPaginationViewset (LimitOffsetPagination):
    default_limit = settings.DEFAULT_LIMIT
    def paginate_queryset(self, queryset, request, view=None):
        if 'limit' not in request.query_params:
            self.limit = None
            return None
        return super().paginate_queryset(queryset, request, view)
    def get_paginated_response(self, data):
        kwargs = {
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link()
        }
        return custom_success_response(data, message='success', status=status.HTTP_200_OK, **kwargs)