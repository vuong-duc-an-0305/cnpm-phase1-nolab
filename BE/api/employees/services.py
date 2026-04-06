"""
Service Layer - Business Logic cho Nhân viên
"""
from django.db.models import Q, Count, Sum, Avg, DecimalField, Value
from .models import NhanVien


class EmployeeService:
    """Service xử lý business logic cho nhân viên"""
    
    @staticmethod
    def get_all_employees(search=None, work_shift=None, job_title=None):
        """
        Lấy danh sách nhân viên với filter
        
        Args:
            search: Tìm kiếm theo tên, SĐT
            work_shift: Lọc theo ca làm việc
            job_title: Lọc theo chức vụ
        """
        queryset = NhanVien.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(FullName__icontains=search) |
                Q(PhoneNumber__icontains=search) |
                Q(JobTitle__icontains=search)
            )
        
        if work_shift:
            queryset = queryset.filter(WorkShift=work_shift)
        
        if job_title:
            queryset = queryset.filter(JobTitle__icontains=job_title)
        
        return queryset.order_by('FullName')
    
    @staticmethod
    def get_employee_by_id(employee_id):
        """Lấy nhân viên theo ID"""
        try:
            return NhanVien.objects.annotate(
                total_orders_handled=Count('hoadon'),
                total_imports_handled=Count('phieunhapkho')
            ).get(EmployeeID=employee_id)
        except NhanVien.DoesNotExist:
            return None
    
    @staticmethod
    def get_employee_by_phone(phone_number):
        """Lấy nhân viên theo số điện thoại"""
        try:
            return NhanVien.objects.get(PhoneNumber=phone_number)
        except NhanVien.DoesNotExist:
            return None
    
    @staticmethod
    def get_employees_by_shift(work_shift):
        """Lấy nhân viên theo ca làm việc"""
        return NhanVien.objects.filter(WorkShift=work_shift).order_by('FullName')
    
    @staticmethod
    def create_employee(employee_data):
        """Tạo nhân viên mới"""
        employee = NhanVien.objects.create(**employee_data)
        return employee
    
    @staticmethod
    def update_employee(employee_id, employee_data):
        """Cập nhật thông tin nhân viên"""
        employee = EmployeeService.get_employee_by_id(employee_id)
        if employee:
            for key, value in employee_data.items():
                if key != 'EmployeeID':
                    setattr(employee, key, value)
            employee.save()
        return employee
    
    @staticmethod
    def delete_employee(employee_id):
        """Xóa nhân viên"""
        employee = EmployeeService.get_employee_by_id(employee_id)
        if employee:
            # Kiểm tra xem có đơn hàng nào không
            if employee.hoadon_set.exists():
                return False, "Không thể xóa nhân viên đã xử lý đơn hàng"
            
            # Kiểm tra xem có phiếu nhập kho nào không
            if employee.phieunhapkho_set.exists():
                return False, "Không thể xóa nhân viên đã xử lý phiếu nhập kho"
            
            employee.delete()
            return True, "Xóa thành công"
        return False, "Không tìm thấy nhân viên"
    
    @staticmethod
    def get_employee_performance(employee_id):
        """
        Lấy thông tin hiệu suất làm việc của nhân viên
        
        Returns:
            dict với thông tin về số đơn hàng, phiếu nhập, tổng doanh thu
        """
        employee = EmployeeService.get_employee_by_id(employee_id)
        if not employee:
            return None
        
        from django.db.models.functions import Coalesce
        
        orders = employee.hoadon_set.all()
        imports = employee.phieunhapkho_set.all()
        
        return {
            'employee_id': employee.EmployeeID,
            'employee_name': employee.FullName,
            'total_orders': orders.count(),
            'total_revenue': orders.aggregate(
                total=Coalesce(Sum('FinalAmount'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
            )['total'],
            'average_order_value': orders.aggregate(
                avg=Coalesce(Avg('FinalAmount'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
            )['avg'],
            'total_imports': imports.count(),
            'total_import_value': imports.aggregate(
                total=Coalesce(Sum('TotalAmount'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
            )['total'],
        }
