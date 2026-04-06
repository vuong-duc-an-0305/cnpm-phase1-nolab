"""
View Layer - API endpoints cho Khách hàng
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.core.permissions import IsAdminRole
from api.core.cache import CachedListMixin

from .models import KhachHang
from .serializers import (
    KhachHangSerializer,
    KhachHangDetailSerializer,
    KhachHangListSerializer,
    LoyaltyPointsUpdateSerializer
)
from .services import CustomerService


class KhachHangViewSet(CachedListMixin, viewsets.ModelViewSet):
    """
    ViewSet cho Khách hàng
    
    Endpoints:
    - GET /api/customers/ - Lấy danh sách khách hàng
    - POST /api/customers/ - Tạo khách hàng mới
    - GET /api/customers/{id}/ - Lấy chi tiết khách hàng
    - PUT /api/customers/{id}/ - Cập nhật khách hàng
    - DELETE /api/customers/{id}/ - Xóa khách hàng
    - GET /api/customers/by-phone/?phone={phone} - Tìm theo SĐT
    - POST /api/customers/{id}/update-points/ - Cập nhật điểm tích lũy
    - GET /api/customers/vip/ - Lấy khách hàng VIP
    - POST /api/customers/{id}/add-points/ - Thêm điểm
    - POST /api/customers/{id}/redeem-points/ - Đổi điểm
    - GET /api/customers/{id}/order-history/ - Lịch sử đơn hàng
    """
    queryset = KhachHang.objects.all()
    serializer_class = KhachHangSerializer
    permission_classes = [IsAdminRole]
    cache_timeout = 300  # 5 minutes
    cache_key_prefix = 'customers'
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action == 'list':
            return KhachHangListSerializer
        elif self.action == 'retrieve':
            return KhachHangDetailSerializer
        return KhachHangSerializer
    
    def get_queryset(self):
        """Override queryset với filter parameters"""
        search = self.request.query_params.get('search')
        membership_level = self.request.query_params.get('membership_level')

        queryset = CustomerService.get_all_customers(search=search)

        # Lọc theo hạng thành viên nếu có
        if membership_level:
            level = str(membership_level).strip().upper()
            if level == 'VIP':
                queryset = queryset.filter(LoyaltyPoints__gte=1000)
            elif level == 'GOLD':
                queryset = queryset.filter(LoyaltyPoints__gte=500, LoyaltyPoints__lt=1000)
            elif level == 'SILVER':
                queryset = queryset.filter(LoyaltyPoints__gte=100, LoyaltyPoints__lt=500)
            elif level == 'BRONZE':
                queryset = queryset.filter(LoyaltyPoints__lt=100)

        return queryset
    
    def create(self, request, *args, **kwargs):
        """Tạo khách hàng mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Kiểm tra SĐT đã tồn tại chưa
        phone = serializer.validated_data.get('PhoneNumber')
        if CustomerService.get_customer_by_phone(phone):
            return Response(
                {'error': 'Số điện thoại đã được đăng ký'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer = CustomerService.create_customer(serializer.validated_data)
        return Response(
            KhachHangDetailSerializer(customer).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Cập nhật khách hàng"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # Kiểm tra SĐT mới đã tồn tại chưa (nếu thay đổi SĐT)
        new_phone = serializer.validated_data.get('PhoneNumber')
        if new_phone and new_phone != instance.PhoneNumber:
            existing_customer = CustomerService.get_customer_by_phone(new_phone)
            if existing_customer and existing_customer.CustomerID != instance.CustomerID:
                return Response(
                    {'error': 'Số điện thoại đã được sử dụng'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        customer = CustomerService.update_customer(instance.CustomerID, serializer.validated_data)
        return Response(KhachHangDetailSerializer(customer).data)
    
    def destroy(self, request, *args, **kwargs):
        """Xóa khách hàng"""
        instance = self.get_object()
        success, message = CustomerService.delete_customer(instance.CustomerID)
        if success:
            # 204 No Content không được phép có body
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def by_phone(self, request):
        """Tìm khách hàng theo số điện thoại"""
        phone = request.query_params.get('phone')
        if not phone:
            return Response(
                {'error': 'Vui lòng cung cấp số điện thoại'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer = CustomerService.get_customer_by_phone(phone)
        if customer:
            serializer = KhachHangDetailSerializer(customer)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Không tìm thấy khách hàng'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def vip(self, request):
        """Lấy danh sách khách hàng VIP"""
        min_points = int(request.query_params.get('min_points', 1000))
        customers = CustomerService.get_vip_customers(min_points)
        serializer = KhachHangListSerializer(customers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """Thêm điểm thành viên"""
        customer = self.get_object()
        serializer = LoyaltyPointsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        points = serializer.validated_data['points']
        if points <= 0:
            return Response(
                {'error': 'Số điểm phải lớn hơn 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, message, updated_customer = CustomerService.update_loyalty_points(
            customer.CustomerID,
            points,
            is_add=True
        )
        
        if success:
            return Response(KhachHangDetailSerializer(updated_customer).data)
        
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def redeem_points(self, request, pk=None):
        """Đổi điểm thành viên (trừ điểm)"""
        customer = self.get_object()
        serializer = LoyaltyPointsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        points = serializer.validated_data['points']
        if points <= 0:
            return Response(
                {'error': 'Số điểm phải lớn hơn 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, message, updated_customer = CustomerService.update_loyalty_points(
            customer.CustomerID,
            points,
            is_add=False
        )
        
        if success:
            return Response(KhachHangDetailSerializer(updated_customer).data)
        
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def order_history(self, request, pk=None):
        """Lấy lịch sử đơn hàng của khách hàng"""
        customer = self.get_object()
        orders = CustomerService.get_customer_order_history(customer.CustomerID)
        
        if orders is not None:
            # Import ở đây để tránh circular import
            from api.orders.serializers import HoaDonListSerializer
            serializer = HoaDonListSerializer(orders, many=True)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Không tìm thấy lịch sử đơn hàng'},
            status=status.HTTP_404_NOT_FOUND
        )
