"""
URL routing cho Employees app
"""
from rest_framework.routers import DefaultRouter
from .views import NhanVienViewSet

router = DefaultRouter()
router.register(r'employees', NhanVienViewSet, basename='employee')
