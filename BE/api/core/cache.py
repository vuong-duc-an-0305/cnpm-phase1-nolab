"""
Cache utilities for API views
"""
from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
import hashlib
import json


def cache_api_response(timeout=300, key_prefix=None):
    """
    Decorator to cache API view responses
    
    Usage:
        @cache_api_response(timeout=600, key_prefix='products')
        def list(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from request
            request = args[1] if len(args) > 1 else kwargs.get('request')
            if not request:
                return func(*args, **kwargs)
            
            # Build cache key from URL, query params, and user
            cache_key_base = f"{key_prefix or func.__name__}:{request.path}"
            query_string = request.GET.urlencode()
            user_id = request.user.id if request.user.is_authenticated else 'anon'
            
            cache_key = f"{cache_key_base}:{user_id}:{hashlib.md5(query_string.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return Response(cached_response)
            
            # Execute view and cache result
            response = func(*args, **kwargs)
            if isinstance(response, Response) and 200 <= response.status_code < 300:
                cache.set(cache_key, response.data, timeout)
            
            return response
        return wrapper
    return decorator


def invalidate_cache(key_patterns):
    """
    Invalidate cache keys matching patterns
    
    Usage:
        invalidate_cache(['products:*', 'categories:*'])
    """
    from django.core.cache import cache
    if hasattr(cache, 'delete_pattern'):
        for pattern in key_patterns:
            cache.delete_pattern(f"coffee_shop:{pattern}")
    else:
        # Fallback for non-Redis backends
        cache.clear()


class CachedListMixin:
    """
    Mixin to add caching to list views
    
    Usage:
        class ProductViewSet(CachedListMixin, viewsets.ModelViewSet):
            cache_timeout = 600
            cache_key_prefix = 'products'
    """
    cache_timeout = 300  # 5 minutes default
    cache_key_prefix = None
    
    def list(self, request, *args, **kwargs):
        # Generate cache key
        prefix = self.cache_key_prefix or self.__class__.__name__
        query_string = request.GET.urlencode()
        user_id = request.user.id if request.user.is_authenticated else 'anon'
        cache_key = f"{prefix}:list:{user_id}:{hashlib.md5(query_string.encode()).hexdigest()}"
        
        # Try cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Get data from DB
        response = super().list(request, *args, **kwargs)
        
        # Cache successful responses
        if response.status_code == 200:
            cache.set(cache_key, response.data, self.cache_timeout)
        
        return response
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Invalidate list cache on create
        if response.status_code in [200, 201]:
            self._invalidate_list_cache()
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Invalidate cache on update
        if response.status_code == 200:
            self._invalidate_list_cache()
            self._invalidate_detail_cache(kwargs.get('pk'))
        return response
    
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        response = super().destroy(request, *args, **kwargs)
        # Invalidate cache on delete
        if response.status_code == 204:
            self._invalidate_list_cache()
            self._invalidate_detail_cache(pk)
        return response
    
    def _invalidate_list_cache(self):
        prefix = self.cache_key_prefix or self.__class__.__name__
        invalidate_cache([f"{prefix}:list:*"])
    
    def _invalidate_detail_cache(self, pk):
        if pk:
            prefix = self.cache_key_prefix or self.__class__.__name__
            invalidate_cache([f"{prefix}:detail:{pk}:*"])
