"""
URL configuration for BE_coffee project.

Coffee Shop Management System API
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    """
    API Root - Tổng quan về các endpoints có sẵn
    """
    return Response({
        'message': 'Chào mừng đến với Coffee Shop Management API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'categories': '/api/categories/',
            'products': '/api/products/',
            'ingredients': '/api/ingredients/',
            'recipes': '/api/recipes/',
            'customers': '/api/customers/',
            'employees': '/api/employees/',
            'orders': '/api/orders/',
            'order_details': '/api/order-details/',
            'inventory': '/api/inventory/',
            'import_details': '/api/import-details/',
        },
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
        }
    })


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API Root
    path('', api_root, name='api-root'),
    
    # API endpoints
    path('api/', include('api.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
