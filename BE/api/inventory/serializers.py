"""
Serializers Layer - Phiếu nhập kho và Chi tiết nhập kho
"""
from rest_framework import serializers
from .models import PhieuNhapKho, ChiTietNhapKho
from api.accounts.serializers import UserSerializer
from api.ingredients.serializers import NguyenLieuSerializer


class ChiTietNhapKhoSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho chi tiết nhập kho"""
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = ChiTietNhapKho
        fields = ['ImportID', 'IngredientID', 'Quantity', 'UnitPrice', 'subtotal']
    
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


class ChiTietNhapKhoDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho chi tiết nhập kho (có thông tin nguyên liệu)"""
    ingredient = NguyenLieuSerializer(source='IngredientID', read_only=True)
    ingredient_name = serializers.CharField(source='IngredientID.IngredientName', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = ChiTietNhapKho
        fields = [
            'ImportID', 'IngredientID', 'ingredient', 'ingredient_name',
            'Quantity', 'UnitPrice', 'subtotal'
        ]


class ChiTietNhapKhoCreateSerializer(serializers.Serializer):
    """Serializer cho việc tạo chi tiết nhập kho"""
    IngredientID = serializers.IntegerField()
    Quantity = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=0.001)
    UnitPrice = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    
    def validate_Quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        return value
    
    def validate_UnitPrice(self, value):
        if value <= 0:
            raise serializers.ValidationError("Đơn giá phải lớn hơn 0")
        return value


class PhieuNhapKhoSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho phiếu nhập kho"""
    
    class Meta:
        model = PhieuNhapKho
        fields = ['ImportID', 'EmployeeID', 'ImportDate', 'TotalAmount']
        read_only_fields = ['ImportID', 'ImportDate', 'TotalAmount']


class PhieuNhapKhoDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho phiếu nhập kho (có thông tin nhân viên, chi tiết)"""
    employee = UserSerializer(source='EmployeeID', read_only=True)
    import_details = ChiTietNhapKhoDetailSerializer(source='chitietnhapkho_set', many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PhieuNhapKho
        fields = [
            'ImportID', 'EmployeeID', 'employee', 'ImportDate',
            'TotalAmount', 'import_details', 'items_count'
        ]
        read_only_fields = ['ImportID', 'ImportDate']


class PhieuNhapKhoListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách phiếu nhập kho (tối ưu performance)"""
    employee_name = serializers.CharField(source='EmployeeID.FullName', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PhieuNhapKho
        fields = [
            'ImportID', 'EmployeeID', 'employee_name',
            'ImportDate', 'TotalAmount', 'items_count'
        ]


class PhieuNhapKhoCreateSerializer(serializers.Serializer):
    """Serializer cho việc tạo phiếu nhập kho mới"""
    EmployeeID = serializers.IntegerField()
    items = serializers.ListField(
        child=ChiTietNhapKhoCreateSerializer(),
        help_text="Danh sách nguyên liệu [{IngredientID, Quantity, UnitPrice}]"
    )
    
    def validate_items(self, value):
        """Validate danh sách nguyên liệu không được trống"""
        if not value:
            raise serializers.ValidationError("Danh sách nguyên liệu không được trống")
        return value
