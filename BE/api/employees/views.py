"""
View Layer - API endpoints cho Nhân viên
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.core.permissions import IsAdminRole

from .models import NhanVien
from .serializers import (
    NhanVienSerializer,
    NhanVienDetailSerializer,
    NhanVienListSerializer
)
from .services import EmployeeService


class NhanVienViewSet(viewsets.ModelViewSet):
    """
    ViewSet cho Nhân viên
    
    Endpoints:
    - GET /api/employees/ - Lấy danh sách nhân viên
    - POST /api/employees/ - Tạo nhân viên mới
    - GET /api/employees/{id}/ - Lấy chi tiết nhân viên
    - PUT /api/employees/{id}/ - Cập nhật nhân viên
    - DELETE /api/employees/{id}/ - Xóa nhân viên
    - GET /api/employees/by-shift/?shift={shift} - Lấy nhân viên theo ca
    - GET /api/employees/{id}/performance/ - Xem hiệu suất làm việc
    """
    queryset = NhanVien.objects.all()
    serializer_class = NhanVienSerializer
    permission_classes = [IsAdminRole]
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp"""
        if self.action == 'list':
            return NhanVienListSerializer
        elif self.action == 'retrieve':
            return NhanVienDetailSerializer
        return NhanVienSerializer
    
    def get_queryset(self):
        """Override queryset với filter parameters"""
        search = self.request.query_params.get('search')
        work_shift = self.request.query_params.get('work_shift')
        job_title = self.request.query_params.get('job_title')
        
        return EmployeeService.get_all_employees(
            search=search,
            work_shift=work_shift,
            job_title=job_title
        )
    
    def create(self, request, *args, **kwargs):
        """Tạo nhân viên mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Kiểm tra SĐT đã tồn tại chưa
        phone = serializer.validated_data.get('PhoneNumber')
        if EmployeeService.get_employee_by_phone(phone):
            return Response(
                {'error': 'Số điện thoại đã được sử dụng'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee = EmployeeService.create_employee(serializer.validated_data)
        return Response(
            NhanVienDetailSerializer(employee).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Cập nhật nhân viên"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # Kiểm tra SĐT mới đã tồn tại chưa (nếu thay đổi SĐT)
        new_phone = serializer.validated_data.get('PhoneNumber')
        if new_phone and new_phone != instance.PhoneNumber:
            existing_employee = EmployeeService.get_employee_by_phone(new_phone)
            if existing_employee and existing_employee.EmployeeID != instance.EmployeeID:
                return Response(
                    {'error': 'Số điện thoại đã được sử dụng'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        employee = EmployeeService.update_employee(instance.EmployeeID, serializer.validated_data)
        return Response(NhanVienDetailSerializer(employee).data)
    
    def destroy(self, request, *args, **kwargs):
        """Xóa nhân viên"""
        instance = self.get_object()
        success, message = EmployeeService.delete_employee(instance.EmployeeID)
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
    def by_shift(self, request):
        """Lấy nhân viên theo ca làm việc"""
        shift = request.query_params.get('shift')
        if not shift:
            return Response(
                {'error': 'Vui lòng cung cấp shift (SANG/CHIEU/TOI/FULL)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employees = EmployeeService.get_employees_by_shift(shift)
        serializer = NhanVienListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Xem hiệu suất làm việc của nhân viên"""
        employee = self.get_object()
        performance_data = EmployeeService.get_employee_performance(employee.EmployeeID)
        
        if performance_data:
            return Response(performance_data)
        
        return Response(
            {'error': 'Không thể lấy thông tin hiệu suất'},
            status=status.HTTP_404_NOT_FOUND
        )
