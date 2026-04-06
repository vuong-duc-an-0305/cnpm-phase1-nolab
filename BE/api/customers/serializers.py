"""
Serializers Layer - Khách hàng
"""
from rest_framework import serializers
from .models import KhachHang
import re


class KhachHangSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho khách hàng"""
    
    class Meta:
        model = KhachHang
        fields = [
            'CustomerID', 'FullName', 'PhoneNumber',
            'Email', 'RegisterDate', 'LoyaltyPoints'
        ]
        read_only_fields = ['CustomerID', 'RegisterDate', 'LoyaltyPoints']
    
    def validate_PhoneNumber(self, value):
        """Validate số điện thoại"""
        if not value or not value.strip():
            raise serializers.ValidationError("Số điện thoại không được để trống")
        
        # Loại bỏ khoảng trắng
        value = value.strip()
        
        # Kiểm tra format số điện thoại Việt Nam (đơn giản)
        if not re.match(r'^(0|\+84)[0-9]{9}$', value):
            raise serializers.ValidationError(
                "Số điện thoại không hợp lệ. Vd: 0901234567 hoặc +84901234567"
            )
        
        return value
    
    def validate_Email(self, value):
        """Validate email"""
        if value:
            value = value.strip().lower()
        return value
    
    def validate_FullName(self, value):
        """Validate họ tên"""
        if not value or not value.strip():
            raise serializers.ValidationError("Họ tên không được để trống")
        return value.strip()


class KhachHangDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho khách hàng"""
    membership_level = serializers.CharField(read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = KhachHang
        fields = [
            'CustomerID', 'FullName', 'PhoneNumber', 'Email',
            'RegisterDate', 'LoyaltyPoints', 'membership_level',
            'total_orders', 'total_spent'
        ]
        read_only_fields = ['CustomerID', 'RegisterDate']


class KhachHangListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách khách hàng"""
    membership_level = serializers.CharField(read_only=True)
    
    class Meta:
        model = KhachHang
        fields = [
            'CustomerID', 'FullName', 'PhoneNumber',
            'Email', 'LoyaltyPoints', 'membership_level'
        ]


class LoyaltyPointsUpdateSerializer(serializers.Serializer):
    """Serializer cho việc cập nhật điểm thành viên"""
    points = serializers.IntegerField(
        required=True,
        help_text="Số điểm cần thêm (số dương) hoặc trừ (số âm)"
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Ghi chú"
    )
