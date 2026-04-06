"""
URL routing cho Customers app
"""
from rest_framework.routers import DefaultRouter
from .views import KhachHangViewSet

router = DefaultRouter()
router.register(r'customers', KhachHangViewSet, basename='customer')
