"""
URL routing cho Recipes app
"""
from rest_framework.routers import DefaultRouter
from .views import CongThucViewSet

router = DefaultRouter()
router.register(r'recipes', CongThucViewSet, basename='recipe')
