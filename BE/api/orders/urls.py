"""
URL routing cho Orders app
"""
from rest_framework.routers import DefaultRouter
from .views import HoaDonViewSet, ChiTietDonHangViewSet

router = DefaultRouter()
router.register(r'orders', HoaDonViewSet, basename='order')
router.register(r'order_details', ChiTietDonHangViewSet, basename='order_detail')
