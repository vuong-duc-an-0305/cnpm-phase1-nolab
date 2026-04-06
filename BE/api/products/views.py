"""
View Layer - API endpoints cho Sản phẩm
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.core.permissions import IsAdminRole
from api.core.cache import CachedListMixin

from .models import SanPham
from .serializers import (
    SanPhamSerializer,
    SanPhamDetailSerializer,
    SanPhamListSerializer,
    SanPhamCreateUpdateSerializer
)
from .services import ProductService


class SanPhamViewSet(CachedListMixin, viewsets.ModelViewSet):
    """
    ViewSet cho Sản phẩm
    
    Endpoints:
    - GET /api/products/ - Lấy danh sách sản phẩm
    - POST /api/products/ - Tạo sản phẩm mới
    - GET /api/products/{id}/ - Lấy chi tiết sản phẩm
    - PUT /api/products/{id}/ - Cập nhật sản phẩm
    - DELETE /api/products/{id}/ - Xóa sản phẩm
    - GET /api/products/available/ - Lấy sản phẩm còn hàng
    - GET /api/products/by-category/?category_id={id} - Lấy sản phẩm theo danh mục
    - POST /api/products/{id}/check-ingredients/ - Kiểm tra nguyên liệu
    - PATCH /api/products/{id}/update-status/ - Cập nhật trạng thái
    """
    queryset = SanPham.objects.select_related('CategoryID').all()
    serializer_class = SanPhamSerializer
    permission_classes = [IsAdminRole]
    cache_timeout = 600  # 10 minutes
    cache_key_prefix = 'products'
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action == 'list':
            return SanPhamListSerializer
        elif self.action == 'retrieve':
            return SanPhamDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SanPhamCreateUpdateSerializer
        return SanPhamSerializer
    
    def get_queryset(self):
        """Override queryset với filter parameters"""
        category_id = self.request.query_params.get('category_id')
        status_param = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        return ProductService.get_all_products(
            category_id=category_id,
            status=status_param,
            search=search
        )
    
    def create(self, request, *args, **kwargs):
        """Tạo sản phẩm mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductService.create_product(serializer.validated_data)
        return Response(
            SanPhamDetailSerializer(product).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Cập nhật sản phẩm"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        product = ProductService.update_product(instance.ProductID, serializer.validated_data)
        return Response(SanPhamDetailSerializer(product).data)
    
    def destroy(self, request, *args, **kwargs):
        """Xóa sản phẩm"""
        instance = self.get_object()
        success, message = ProductService.delete_product(instance.ProductID)
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
    def available(self, request):
        """Lấy danh sách sản phẩm còn hàng"""
        products = ProductService.get_available_products()
        serializer = SanPhamListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Lấy sản phẩm theo danh mục"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'Vui lòng cung cấp category_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = ProductService.get_products_by_category(category_id)
        serializer = SanPhamListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_ingredients(self, request, pk=None):
        """Kiểm tra nguyên liệu có đủ để làm sản phẩm không"""
        product = self.get_object()
        quantity = request.data.get('quantity', 1)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'Số lượng phải lớn hơn 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Số lượng không hợp lệ'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_available, missing = ProductService.check_ingredients_availability(product.ProductID, quantity)
        
        return Response({
            'product_id': product.ProductID,
            'product_name': product.ProductName,
            'quantity': quantity,
            'is_available': is_available,
            'missing_ingredients': missing if not is_available else []
        })
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Cập nhật trạng thái sản phẩm"""
        product = self.get_object()
        new_status = request.data.get('status')
        
        if new_status is None:
            return Response(
                {'error': 'Vui lòng cung cấp status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_status = int(new_status)
            if new_status not in [0, 1, 2]:
                raise ValueError
        except ValueError:
            return Response(
                {'error': 'Status phải là 0 (Hết hàng), 1 (Còn hàng), hoặc 2 (Ngừng kinh doanh)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, updated_product = ProductService.update_product_status(product.ProductID, new_status)
        
        if success:
            return Response(SanPhamDetailSerializer(updated_product).data)
        
        return Response(
            {'error': 'Không thể cập nhật trạng thái'},
            status=status.HTTP_400_BAD_REQUEST
        )
