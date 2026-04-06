"""
URL routing cho Ingredients app
"""
from rest_framework.routers import DefaultRouter
from .views import NguyenLieuViewSet

router = DefaultRouter()
router.register(r'ingredients', NguyenLieuViewSet, basename='ingredient')
