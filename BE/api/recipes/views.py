"""
View Layer - API endpoints cho Công thức
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.core.permissions import IsAdminRole

from .models import CongThuc
from .serializers import (
    CongThucSerializer,
    CongThucDetailSerializer,
    CongThucListSerializer,
    CongThucCreateSerializer
)
from .services import RecipeService


class CongThucViewSet(viewsets.ModelViewSet):
    """
    ViewSet cho Công thức
    
    Endpoints:
    - GET /api/recipes/ - Lấy danh sách công thức
    - POST /api/recipes/ - Tạo công thức mới
    - GET /api/recipes/by-product/?product_id={id} - Lấy công thức theo sản phẩm
    - GET /api/recipes/by-ingredient/?ingredient_id={id} - Lấy sản phẩm dùng nguyên liệu
    - POST /api/recipes/bulk-create/ - Tạo nhiều công thức cho 1 sản phẩm
    - DELETE /api/recipes/delete-by-product/?product_id={id} - Xóa công thức của sản phẩm
    """
    queryset = CongThuc.objects.all()
    serializer_class = CongThucSerializer
    permission_classes = [IsAdminRole]
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action == 'list':
            return CongThucListSerializer
        elif self.action == 'retrieve':
            return CongThucDetailSerializer
        elif self.action == 'bulk_create':
            return CongThucCreateSerializer
        return CongThucSerializer
    
    def get_queryset(self):
        """Override queryset với filter parameters"""
        product_id = self.request.query_params.get('product_id')
        ingredient_id = self.request.query_params.get('ingredient_id')
        
        return RecipeService.get_all_recipes(
            product_id=product_id,
            ingredient_id=ingredient_id
        )
    
    def create(self, request, *args, **kwargs):
        """Tạo công thức mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = RecipeService.create_recipe(serializer.validated_data)
        return Response(
            CongThucDetailSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Cập nhật công thức"""
        # Lấy ProductID và IngredientID từ request
        product_id = request.data.get('ProductID')
        ingredient_id = request.data.get('IngredientID')
        
        if not product_id or not ingredient_id:
            return Response(
                {'error': 'Vui lòng cung cấp ProductID và IngredientID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        recipe = RecipeService.update_recipe(
            product_id,
            ingredient_id,
            serializer.validated_data
        )
        
        if recipe:
            return Response(CongThucDetailSerializer(recipe).data)
        
        return Response(
            {'error': 'Không tìm thấy công thức'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Lấy công thức theo sản phẩm"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'Vui lòng cung cấp product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recipes = RecipeService.get_recipes_by_product(product_id)
        serializer = CongThucListSerializer(recipes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_ingredient(self, request):
        """Lấy sản phẩm sử dụng nguyên liệu"""
        ingredient_id = request.query_params.get('ingredient_id')
        if not ingredient_id:
            return Response(
                {'error': 'Vui lòng cung cấp ingredient_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recipes = RecipeService.get_products_using_ingredient(ingredient_id)
        serializer = CongThucListSerializer(recipes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Tạo nhiều công thức cho một sản phẩm"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['ProductID']
        ingredients_list = serializer.validated_data['ingredients']
        
        success, message, recipes = RecipeService.create_recipes_bulk(
            product_id,
            ingredients_list
        )
        
        if success:
            return Response(
                {
                    'message': message,
                    'recipes': CongThucListSerializer(recipes, many=True).data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['delete'])
    def delete_by_product(self, request):
        """Xóa tất cả công thức của một sản phẩm"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'Vui lòng cung cấp product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = RecipeService.delete_recipes_by_product(product_id)
        return Response(
            {
                'message': f'Đã xóa {deleted_count} công thức',
                'deleted_count': deleted_count
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def check_completeness(self, request):
        """Kiểm tra sản phẩm có đủ công thức không"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'Vui lòng cung cấp product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_recipe, count, ingredients = RecipeService.check_recipe_completeness(product_id)
        
        return Response({
            'product_id': product_id,
            'has_recipe': has_recipe,
            'recipe_count': count,
            'ingredients': ingredients
        })
