"""
View Layer - API endpoints cho Phiếu nhập kho
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.core.permissions import IsAdminRole
from datetime import datetime

from .models import PhieuNhapKho, ChiTietNhapKho
from .serializers import (
    PhieuNhapKhoSerializer,
    PhieuNhapKhoDetailSerializer,
    PhieuNhapKhoListSerializer,
    PhieuNhapKhoCreateSerializer,
    ChiTietNhapKhoSerializer,
    ChiTietNhapKhoDetailSerializer
)
from .services import InventoryService


class PhieuNhapKhoViewSet(viewsets.ModelViewSet):
    """
    ViewSet cho Phiếu nhập kho
    
    Endpoints:
    - GET /api/inventory/ - Lấy danh sách phiếu nhập kho
    - POST /api/inventory/ - Tạo phiếu nhập kho mới
    - GET /api/inventory/{id}/ - Lấy chi tiết phiếu nhập kho
    - DELETE /api/inventory/{id}/ - Xóa phiếu nhập kho
    - GET /api/inventory/statistics/ - Thống kê nhập kho
    - GET /api/inventory/ingredient-history/?ingredient_id={id} - Lịch sử nhập nguyên liệu
    """
    queryset = PhieuNhapKho.objects.all()
    serializer_class = PhieuNhapKhoSerializer
    permission_classes = [IsAdminRole]
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action == 'list':
            return PhieuNhapKhoListSerializer
        elif self.action == 'retrieve':
            return PhieuNhapKhoDetailSerializer
        elif self.action == 'create':
            return PhieuNhapKhoCreateSerializer
        return PhieuNhapKhoSerializer
    
    def get_queryset(self):
        """Override queryset với filter parameters"""
        employee_id = self.request.query_params.get('employee_id')
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
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
        
        return InventoryService.get_all_imports(
            employee_id=employee_id,
            from_date=from_date_obj,
            to_date=to_date_obj
        )
    
    def create(self, request, *args, **kwargs):
        """Tạo phiếu nhập kho mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        import_data = {
            'EmployeeID': serializer.validated_data['EmployeeID']
        }
        
        items_data = serializer.validated_data['items']
        
        success, result, errors = InventoryService.create_import(import_data, items_data)
        
        if success:
            return Response(
                PhieuNhapKhoDetailSerializer(result).data,
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
        """Không cho phép cập nhật phiếu nhập kho"""
        return Response(
            {'error': 'Không thể cập nhật phiếu nhập kho. Vui lòng xóa và tạo mới nếu cần.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Xóa phiếu nhập kho"""
        instance = self.get_object()
        success, message = InventoryService.delete_import(instance.ImportID)
        
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
    def statistics(self, request):
        """Thống kê nhập kho"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
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
        
        stats = InventoryService.get_import_statistics(from_date_obj, to_date_obj)
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def ingredient_history(self, request):
        """Lấy lịch sử nhập kho của nguyên liệu"""
        ingredient_id = request.query_params.get('ingredient_id')
        if not ingredient_id:
            return Response(
                {'error': 'Vui lòng cung cấp ingredient_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = InventoryService.get_ingredient_import_history(ingredient_id)
        serializer = ChiTietNhapKhoDetailSerializer(history, many=True)
        return Response(serializer.data)


class ChiTietNhapKhoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet cho Chi tiết nhập kho (Chỉ đọc)
    
    Endpoints:
    - GET /api/import-details/ - Lấy danh sách chi tiết nhập kho
    - GET /api/import-details/{id}/ - Lấy chi tiết
    """
    queryset = ChiTietNhapKho.objects.all()
    serializer_class = ChiTietNhapKhoSerializer
    permission_classes = [IsAdminRole]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChiTietNhapKhoDetailSerializer
        return ChiTietNhapKhoSerializer
    
    def get_queryset(self):
        """Override queryset với filter"""
        import_id = self.request.query_params.get('import_id')
        ingredient_id = self.request.query_params.get('ingredient_id')
        
        queryset = ChiTietNhapKho.objects.select_related(
            'ImportID__EmployeeID',
            'IngredientID'
        ).all()
        
        if import_id:
            queryset = queryset.filter(ImportID=import_id)
        
        if ingredient_id:
            queryset = queryset.filter(IngredientID=ingredient_id)
        
        return queryset.order_by('-ImportID__ImportDate')
