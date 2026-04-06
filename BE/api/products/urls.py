"""
URL routing cho Products app
"""
from rest_framework.routers import DefaultRouter
from .views import SanPhamViewSet

router = DefaultRouter()
router.register(r'products', SanPhamViewSet, basename='product')
