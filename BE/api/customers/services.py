"""
Service Layer - Business Logic cho Khách hàng
"""
from django.db.models import Q, Count, Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from .models import KhachHang


class CustomerService:
    """Service xử lý business logic cho khách hàng"""
    
    @staticmethod
    def get_all_customers(search=None):
        """
        Lấy danh sách khách hàng với tìm kiếm
        
        Args:
            search: Tìm kiếm theo tên, SĐT, email
        """
        queryset = KhachHang.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(FullName__icontains=search) |
                Q(PhoneNumber__icontains=search) |
                Q(Email__icontains=search)
            )
        
        return queryset.order_by('-RegisterDate')
    
    @staticmethod
    def get_customer_by_id(customer_id):
        """Lấy khách hàng theo ID"""
        try:
            return KhachHang.objects.annotate(
                total_orders=Count('hoadon'),
                total_spent=Coalesce(
                    Sum('hoadon__FinalAmount'),
                    Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
                )
            ).get(CustomerID=customer_id)
        except KhachHang.DoesNotExist:
            return None
    
    @staticmethod
    def get_customer_by_phone(phone_number):
        """Lấy khách hàng theo số điện thoại"""
        try:
            return KhachHang.objects.get(PhoneNumber=phone_number)
        except KhachHang.DoesNotExist:
            return None
    
    @staticmethod
    def get_customer_by_email(email):
        """Lấy khách hàng theo email"""
        try:
            return KhachHang.objects.get(Email=email)
        except KhachHang.DoesNotExist:
            return None
    
    @staticmethod
    def create_customer(customer_data):
        """Tạo khách hàng mới"""
        customer = KhachHang.objects.create(**customer_data)
        return customer
    
    @staticmethod
    def update_customer(customer_id, customer_data):
        """Cập nhật thông tin khách hàng"""
        customer = CustomerService.get_customer_by_id(customer_id)
        if customer:
            for key, value in customer_data.items():
                if key not in ['CustomerID', 'RegisterDate', 'LoyaltyPoints']:
                    setattr(customer, key, value)
            customer.save()
        return customer
    
    @staticmethod
    def delete_customer(customer_id):
        """Xóa khách hàng"""
        customer = CustomerService.get_customer_by_id(customer_id)
        if customer:
            # Kiểm tra xem có đơn hàng nào không
            if customer.hoadon_set.exists():
                return False, "Không thể xóa khách hàng đã có đơn hàng"
            
            customer.delete()
            return True, "Xóa thành công"
        return False, "Không tìm thấy khách hàng"
    
    @staticmethod
    def update_loyalty_points(customer_id, points, is_add=True):
        """
        Cập nhật điểm thành viên
        
        Args:
            customer_id: ID khách hàng
            points: Số điểm cần thêm/trừ
            is_add: True = cộng, False = trừ
        
        Returns:
            (success, message, customer)
        """
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            return False, "Không tìm thấy khách hàng", None
        
        if is_add:
            customer.LoyaltyPoints += points
        else:
            if customer.LoyaltyPoints < points:
                return False, "Số điểm không đủ", None
            customer.LoyaltyPoints -= points
        
        # Đảm bảo điểm không âm
        if customer.LoyaltyPoints < 0:
            customer.LoyaltyPoints = 0
        
        customer.save()
        return True, "Cập nhật điểm thành công", customer
    
    @staticmethod
    def add_points_from_order(customer_id, order_amount):
        """
        Tự động cộng điểm từ đơn hàng
        Qui tắc: Mỗi 10,000đ = 1 điểm
        
        Args:
            customer_id: ID khách hàng
            order_amount: Số tiền đơn hàng
        
        Returns:
            (success, points_added, customer)
        """
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            return False, 0, None
        
        # Tính điểm: 10,000đ = 1 điểm
        points_to_add = int(order_amount / 10000)
        
        if points_to_add > 0:
            customer.LoyaltyPoints += points_to_add
            customer.save()
        
        return True, points_to_add, customer
    
    @staticmethod
    def get_vip_customers(min_points=1000):
        """Lấy danh sách khách hàng VIP"""
        return KhachHang.objects.filter(
            LoyaltyPoints__gte=min_points
        ).order_by('-LoyaltyPoints')
    
    @staticmethod
    def get_customer_order_history(customer_id):
        """Lấy lịch sử đơn hàng của khách hàng"""
        customer = CustomerService.get_customer_by_id(customer_id)
        if customer:
            return customer.hoadon_set.select_related('EmployeeID').order_by('-OrderDate')
        return None
