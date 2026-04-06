"""
View Layer - API endpoints cho Nguyên liệu
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.core.permissions import IsAdminRole
from api.core.cache import CachedListMixin

from .models import NguyenLieu
from .serializers import (
    NguyenLieuSerializer,
    NguyenLieuDetailSerializer,
    NguyenLieuStockUpdateSerializer
)
from .services import IngredientService


class NguyenLieuViewSet(CachedListMixin, viewsets.ModelViewSet):
    """
    ViewSet cho Nguyên liệu
    
    Endpoints:
    - GET /api/ingredients/ - Lấy danh sách nguyên liệu
    - POST /api/ingredients/ - Tạo nguyên liệu mới
    - GET /api/ingredients/{id}/ - Lấy chi tiết nguyên liệu
    - PUT /api/ingredients/{id}/ - Cập nhật nguyên liệu
    - DELETE /api/ingredients/{id}/ - Xóa nguyên liệu
    - GET /api/ingredients/low-stock/ - Lấy nguyên liệu sắp hết
    - POST /api/ingredients/{id}/add-stock/ - Thêm vào kho
    - POST /api/ingredients/{id}/reduce-stock/ - Trừ khỏi kho
    """
    queryset = NguyenLieu.objects.all()
    serializer_class = NguyenLieuSerializer
    permission_classes = [IsAdminRole]
    cache_timeout = 600  # 10 minutes
    cache_key_prefix = 'ingredients'
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action in ['retrieve', 'list']:
            return NguyenLieuDetailSerializer
        return NguyenLieuSerializer
    
    def get_queryset(self):
        """Override queryset với filter parameters"""
        search = self.request.query_params.get('search')
        return IngredientService.get_all_ingredients(search=search)
    
    def create(self, request, *args, **kwargs):
        """Tạo nguyên liệu mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ingredient = IngredientService.create_ingredient(serializer.validated_data)
        return Response(
            NguyenLieuDetailSerializer(ingredient).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Cập nhật nguyên liệu"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        ingredient = IngredientService.update_ingredient(instance.IngredientID, serializer.validated_data)
        return Response(NguyenLieuDetailSerializer(ingredient).data)
    
    def destroy(self, request, *args, **kwargs):
        """Xóa nguyên liệu"""
        instance = self.get_object()
        success, message = IngredientService.delete_ingredient(instance.IngredientID)
        if success:
            return Response(
                {'message': message},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Lấy danh sách nguyên liệu sắp hết"""
        ingredients = IngredientService.get_low_stock_ingredients()
        serializer = NguyenLieuDetailSerializer(ingredients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """Thêm nguyên liệu vào kho"""
        ingredient = self.get_object()
        serializer = NguyenLieuStockUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data['quantity']
        if quantity <= 0:
            return Response(
                {'error': 'Số lượng phải lớn hơn 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, message, updated_ingredient = IngredientService.update_stock(
            ingredient.IngredientID,
            quantity,
            is_add=True
        )
        
        if success:
            return Response(NguyenLieuDetailSerializer(updated_ingredient).data)
        
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, pk=None):
        """Trừ nguyên liệu khỏi kho"""
        ingredient = self.get_object()
        serializer = NguyenLieuStockUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data['quantity']
        if quantity <= 0:
            return Response(
                {'error': 'Số lượng phải lớn hơn 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, message, updated_ingredient = IngredientService.update_stock(
            ingredient.IngredientID,
            quantity,
            is_add=False
        )
        
        if success:
            return Response(NguyenLieuDetailSerializer(updated_ingredient).data)
        
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
