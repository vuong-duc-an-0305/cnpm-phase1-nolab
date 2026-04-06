"""
URL routing cho Categories app
"""
from rest_framework.routers import DefaultRouter
from .views import DanhMucSanPhamViewSet

router = DefaultRouter()
router.register(r'categories', DanhMucSanPhamViewSet, basename='category')
