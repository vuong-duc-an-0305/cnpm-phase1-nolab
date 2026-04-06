"""
URL routing cho Inventory app
"""
from rest_framework.routers import DefaultRouter
from .views import PhieuNhapKhoViewSet, ChiTietNhapKhoViewSet

router = DefaultRouter()
router.register(r'inventory', PhieuNhapKhoViewSet, basename='inventory')
router.register(r'import-details', ChiTietNhapKhoViewSet, basename='import-detail')
