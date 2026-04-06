"""
Serializers Layer - Hóa đơn và Chi tiết đơn hàng
"""
from rest_framework import serializers
from .models import HoaDon, ChiTietDonHang
from api.customers.serializers import KhachHangSerializer
from api.accounts.serializers import UserSerializer
from api.products.serializers import SanPhamSerializer


class ChiTietDonHangSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho chi tiết đơn hàng"""
    
    class Meta:
        model = ChiTietDonHang
        fields = [
            'OrderDetailID', 'OrderID', 'ProductID',
            'Quantity', 'UnitPrice', 'Subtotal', 'ToppingNote'
        ]
        read_only_fields = ['OrderDetailID', 'Subtotal']
    
    def validate_Quantity(self, value):
        """Validate số lượng phải lớn hơn 0"""
        if value <= 0:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        return value
    
    def validate_UnitPrice(self, value):
        """Validate đơn giá phải lớn hơn 0"""
        if value <= 0:
            raise serializers.ValidationError("Đơn giá phải lớn hơn 0")
        return value


class ChiTietDonHangDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho chi tiết đơn hàng (có thông tin sản phẩm)"""
    product = SanPhamSerializer(source='ProductID', read_only=True)
    product_name = serializers.CharField(source='ProductID.ProductName', read_only=True)
    
    class Meta:
        model = ChiTietDonHang
        fields = [
            'OrderDetailID', 'OrderID', 'ProductID', 'product', 'product_name',
            'Quantity', 'UnitPrice', 'Subtotal', 'ToppingNote'
        ]
        read_only_fields = ['OrderDetailID', 'Subtotal']


class ChiTietDonHangCreateSerializer(serializers.Serializer):
    """Serializer cho việc tạo chi tiết đơn hàng"""
    ProductID = serializers.IntegerField()
    Quantity = serializers.IntegerField(min_value=1)
    ToppingNote = serializers.CharField(required=False, allow_blank=True, max_length=200)
    
    def validate_Quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        return value


class HoaDonSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho hóa đơn"""
    
    class Meta:
        model = HoaDon
        fields = [
            'OrderID', 'CustomerID', 'EmployeeID', 'OrderDate',
            'TotalAmount', 'Discount', 'FinalAmount',
            'PaymentMethod', 'Status'
        ]
        read_only_fields = ['OrderID', 'OrderDate', 'TotalAmount', 'FinalAmount']
    
    def validate_Discount(self, value):
        """Validate giảm giá không âm"""
        if value < 0:
            raise serializers.ValidationError("Giảm giá không được âm")
        return value


class HoaDonDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho hóa đơn (có thông tin khách hàng, nhân viên, chi tiết)"""
    customer = KhachHangSerializer(source='CustomerID', read_only=True)
    employee = UserSerializer(source='EmployeeID', read_only=True)
    order_details = ChiTietDonHangDetailSerializer(source='chitietdonhang_set', many=True, read_only=True)
    status_display = serializers.CharField(source='get_Status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_PaymentMethod_display', read_only=True)
    
    class Meta:
        model = HoaDon
        fields = [
            'OrderID', 'CustomerID', 'customer', 'EmployeeID', 'employee',
            'OrderDate', 'TotalAmount', 'Discount', 'FinalAmount',
            'PaymentMethod', 'payment_method_display',
            'Status', 'status_display', 'order_details'
        ]
        read_only_fields = ['OrderID', 'OrderDate']


class HoaDonListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách hóa đơn (tối ưu performance)"""
    customer_name = serializers.CharField(source='CustomerID.FullName', read_only=True)
    employee_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_Status_display', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    
    def get_employee_name(self, obj):
        if obj.EmployeeID:
            full_name = f"{obj.EmployeeID.first_name} {obj.EmployeeID.last_name}".strip()
            return full_name if full_name else obj.EmployeeID.username
        return None
    
    class Meta:
        model = HoaDon
        fields = [
            'OrderID', 'CustomerID', 'customer_name',
            'EmployeeID', 'employee_name', 'OrderDate',
            'TotalAmount', 'Discount', 'FinalAmount',
            'PaymentMethod', 'Status', 'status_display', 'items_count'
        ]


class HoaDonCreateSerializer(serializers.Serializer):
    """Serializer cho việc tạo hóa đơn mới"""
    CustomerID = serializers.IntegerField(required=False, allow_null=True)
    EmployeeID = serializers.IntegerField()
    PaymentMethod = serializers.ChoiceField(choices=HoaDon.PAYMENT_METHOD_CHOICES, default='CASH')
    Discount = serializers.DecimalField(max_digits=12, decimal_places=2, default=0, min_value=0)
    items = serializers.ListField(
        child=ChiTietDonHangCreateSerializer(),
        help_text="Danh sách sản phẩm [{ProductID, Quantity, ToppingNote}]"
    )
    
    def validate_items(self, value):
        """Validate danh sách sản phẩm không được trống"""
        if not value:
            raise serializers.ValidationError("Danh sách sản phẩm không được trống")
        return value
    
    def validate(self, attrs):
        """Validate toàn bộ dữ liệu"""
        # Kiểm tra Discount không lớn hơn TotalAmount (sẽ tính sau)
        return attrs


class HoaDonUpdateStatusSerializer(serializers.Serializer):
    """Serializer cho việc cập nhật trạng thái đơn hàng"""
    Status = serializers.ChoiceField(choices=HoaDon.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)
