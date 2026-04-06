"""
View Layer - API endpoints cho Hóa đơn và Chi tiết đơn hàng
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from api.core.permissions import IsAdminOrCashierRole

from .models import HoaDon, ChiTietDonHang
from .serializers import (
    HoaDonSerializer,
    HoaDonDetailSerializer,
    HoaDonListSerializer,
    HoaDonCreateSerializer,
    HoaDonUpdateStatusSerializer,
    ChiTietDonHangSerializer,
    ChiTietDonHangDetailSerializer
)
from .services import OrderService


class HoaDonViewSet(viewsets.ModelViewSet):
    """
    ViewSet cho Hóa đơn
    
    Endpoints:
    - GET /api/orders/ - Lấy danh sách đơn hàng
    - POST /api/orders/ - Tạo đơn hàng mới
    - GET /api/orders/{id}/ - Lấy chi tiết đơn hàng
    - DELETE /api/orders/{id}/ - Xóa đơn hàng
    - PATCH /api/orders/{id}/update-status/ - Cập nhật trạng thái
    - GET /api/orders/revenue-stats/ - Thống kê doanh thu
    - GET /api/orders/best-selling/ - Sản phẩm bán chạy
    - GET /api/orders/by-customer/?customer_id={id} - Đơn hàng của khách
    - GET /api/orders/by-status/?status={status} - Lọc theo trạng thái
    """
    queryset = HoaDon.objects.all()
    serializer_class = HoaDonSerializer
    permission_classes = [IsAdminOrCashierRole]
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action == 'list':
            return HoaDonListSerializer
        elif self.action == 'retrieve':
            return HoaDonDetailSerializer
        elif self.action == 'create':
            return HoaDonCreateSerializer
        elif self.action == 'update_status':
            return HoaDonUpdateStatusSerializer
        return HoaDonSerializer
    
    def get_queryset(self):
        """Override queryset với filter parameters"""
        customer_id = self.request.query_params.get('customer_id')
        employee_id = self.request.query_params.get('employee_id')
        status_param = self.request.query_params.get('status')
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        search = self.request.query_params.get('search')
        
        # Parse dates
        from_date_obj = None
        to_date_obj = None
        
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        return OrderService.get_all_orders(
            customer_id=customer_id,
            employee_id=employee_id,
            status=status_param,
            from_date=from_date_obj,
            to_date=to_date_obj,
            search=search
        )
    
    def create(self, request, *args, **kwargs):
        """Tạo đơn hàng mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_data = {
            'CustomerID': serializer.validated_data.get('CustomerID'),
            'EmployeeID': serializer.validated_data['EmployeeID'],
            'PaymentMethod': serializer.validated_data.get('PaymentMethod', 'CASH'),
            'Discount': serializer.validated_data.get('Discount', 0),
        }
        
        items_data = serializer.validated_data['items']
        
        success, result, errors = OrderService.create_order(order_data, items_data)
        
        if success:
            return Response(
                HoaDonDetailSerializer(result).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                'error': result,
                'details': errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def update(self, request, *args, **kwargs):
        """Không cho phép cập nhật trực tiếp, dùng update_status"""
        return Response(
            {'error': 'Không thể cập nhật đơn hàng trực tiếp. Sử dụng endpoint update-status để thay đổi trạng thái.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Xóa đơn hàng"""
        instance = self.get_object()
        success, message = OrderService.delete_order(instance.OrderID)
        
        if success:
            return Response(
                {'message': message},
                status=status.HTTP_204_NO_CONTENT
            )
        
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['patch'], url_path='update_status')
    def update_status(self, request, pk=None):
        """Cập nhật trạng thái đơn hàng"""
        order = self.get_object()
        serializer = HoaDonUpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['Status']
        
        success, message, updated_order = OrderService.update_order_status(
            order.OrderID,
            new_status
        )
        
        if success:
            return Response(HoaDonDetailSerializer(updated_order).data)
        
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'], url_path='revenue_stats')
    def revenue_stats(self, request):
        """Thống kê doanh thu"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        include_all_status = request.query_params.get('include_all_status', 'false').lower() == 'true'
        
        from_date_obj = None
        to_date_obj = None
        
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'from_date phải có định dạng YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'to_date phải có định dạng YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        stats = OrderService.get_revenue_statistics(from_date_obj, to_date_obj, include_all_status)
        return Response(stats)
    
    @action(detail=False, methods=['get'], url_path='best_selling')
    def best_selling(self, request):
        """Lấy sản phẩm bán chạy nhất"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        limit = int(request.query_params.get('limit', 10))
        
        from_date_obj = None
        to_date_obj = None
        
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        products = OrderService.get_best_selling_products(
            from_date_obj,
            to_date_obj,
            limit
        )
        
        return Response({
            'best_selling_products': products,
            'from_date': from_date,
            'to_date': to_date
        })

    @action(detail=False, methods=['get'], url_path='revenue_trend')
    def revenue_trend(self, request):
        """Dữ liệu doanh thu theo thời gian (day|week|month)"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        interval = request.query_params.get('interval', 'day')

        from_date_obj = None
        to_date_obj = None
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'from_date phải có định dạng YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'to_date phải có định dạng YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        data = OrderService.get_revenue_trend(from_date_obj, to_date_obj, interval)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='revenue_by_category')
    def revenue_by_category(self, request):
        """Tổng doanh thu theo danh mục"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        from_date_obj = None
        to_date_obj = None
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'from_date phải có định dạng YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'to_date phải có định dạng YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        data = OrderService.get_revenue_by_category(from_date_obj, to_date_obj)
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='by_customer')
    def by_customer(self, request):
        """Lấy đơn hàng của khách hàng"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'Vui lòng cung cấp customer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = OrderService.get_all_orders(customer_id=customer_id)
        serializer = HoaDonListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by_status')
    def by_status(self, request):
        """Lấy đơn hàng theo trạng thái"""
        status_param = request.query_params.get('status')
        if not status_param:
            return Response(
                {'error': 'Vui lòng cung cấp status (PENDING/PREPARING/COMPLETED/CANCELLED)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = OrderService.get_all_orders(status=status_param)
        serializer = HoaDonListSerializer(orders, many=True)
        return Response(serializer.data)


class ChiTietDonHangViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet cho Chi tiết đơn hàng (Chỉ đọc)
    
    Endpoints:
    - GET /api/order-details/ - Lấy danh sách chi tiết đơn hàng
    - GET /api/order-details/{id}/ - Lấy chi tiết
    """
    queryset = ChiTietDonHang.objects.all()
    serializer_class = ChiTietDonHangSerializer
    permission_classes = [IsAdminOrCashierRole]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChiTietDonHangDetailSerializer
        return ChiTietDonHangSerializer
    
    def get_queryset(self):
        """Override queryset với filter"""
        order_id = self.request.query_params.get('order_id')
        product_id = self.request.query_params.get('product_id')
        
        queryset = ChiTietDonHang.objects.select_related(
            'OrderID',
            'ProductID'
        ).all()
        
        if order_id:
            queryset = queryset.filter(OrderID=order_id)
        
        if product_id:
            queryset = queryset.filter(ProductID=product_id)
        
        return queryset.order_by('-OrderID__OrderDate')
