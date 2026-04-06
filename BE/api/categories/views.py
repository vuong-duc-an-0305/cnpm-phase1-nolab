""" 
View Layer - API endpoints cho Danh mục sản phẩm
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.core.permissions import IsAdminRole
from api.core.cache import CachedListMixin

from .models import DanhMucSanPham
from .serializers import DanhMucSanPhamSerializer, DanhMucSanPhamListSerializer
from .services import CategoryService


class DanhMucSanPhamViewSet(CachedListMixin, viewsets.ModelViewSet):
    """
    ViewSet cho Danh mục sản phẩm
    
    Endpoints:
    - GET /api/categories/ - Lấy danh sách danh mục
    - POST /api/categories/ - Tạo danh mục mới
    - GET /api/categories/{id}/ - Lấy chi tiết danh mục
    - PUT /api/categories/{id}/ - Cập nhật danh mục
    - DELETE /api/categories/{id}/ - Xóa danh mục
    - GET /api/categories/with-product-count/ - Lấy danh sách kèm số sản phẩm
    """
    queryset = DanhMucSanPham.objects.all()
    serializer_class = DanhMucSanPhamSerializer
    permission_classes = [IsAdminRole]
    cache_timeout = 900  # 15 minutes
    cache_key_prefix = 'categories'
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action == 'list':
            return DanhMucSanPhamListSerializer
        return DanhMucSanPhamSerializer
    
    def get_queryset(self):
        """Override queryset để thêm product_count cho list action"""
        if self.action == 'list':
            return CategoryService.get_all_categories_with_product_count()
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        """Tạo danh mục mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = CategoryService.create_category(serializer.validated_data)
        return Response(
            DanhMucSanPhamSerializer(category).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Cập nhật danh mục"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        category = CategoryService.update_category(instance.CategoryID, serializer.validated_data)
        return Response(DanhMucSanPhamSerializer(category).data)
    
    def destroy(self, request, *args, **kwargs):
        """Xóa danh mục"""
        instance = self.get_object()
        success, message = CategoryService.delete_category(instance.CategoryID)
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
    def with_product_count(self, request):
        """Lấy danh sách danh mục kèm số lượng sản phẩm"""
        categories = CategoryService.get_all_categories_with_product_count()
        serializer = DanhMucSanPhamListSerializer(categories, many=True)
        return Response(serializer.data)
