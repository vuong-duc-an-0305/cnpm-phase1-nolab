"""
Serializers Layer - Nhân viên
"""
from rest_framework import serializers
from .models import NhanVien
import re


class NhanVienSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho nhân viên"""
    
    class Meta:
        model = NhanVien
        fields = [
            'EmployeeID', 'FullName', 'PhoneNumber',
            'JobTitle', 'WorkShift'
        ]
        read_only_fields = ['EmployeeID']
    
    def validate_PhoneNumber(self, value):
        """Validate số điện thoại"""
        if not value or not value.strip():
            raise serializers.ValidationError("Số điện thoại không được để trống")
        
        value = value.strip()
        
        if not re.match(r'^(0|\+84)[0-9]{9}$', value):
            raise serializers.ValidationError(
                "Số điện thoại không hợp lệ. Vd: 0901234567 hoặc +84901234567"
            )
        
        return value
    
    def validate_FullName(self, value):
        """Validate họ tên"""
        if not value or not value.strip():
            raise serializers.ValidationError("Họ tên không được để trống")
        return value.strip()
    
    def validate_JobTitle(self, value):
        """Validate chức vụ"""
        if not value or not value.strip():
            raise serializers.ValidationError("Chức vụ không được để trống")
        return value.strip()


class NhanVienDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho nhân viên"""
    work_shift_display = serializers.CharField(source='get_WorkShift_display', read_only=True)
    total_orders_handled = serializers.IntegerField(read_only=True)
    total_imports_handled = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = NhanVien
        fields = [
            'EmployeeID', 'FullName', 'PhoneNumber',
            'JobTitle', 'WorkShift', 'work_shift_display',
            'total_orders_handled', 'total_imports_handled'
        ]
        read_only_fields = ['EmployeeID']


class NhanVienListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách nhân viên"""
    work_shift_display = serializers.CharField(source='get_WorkShift_display', read_only=True)
    
    class Meta:
        model = NhanVien
        fields = [
            'EmployeeID', 'FullName', 'PhoneNumber',
            'JobTitle', 'WorkShift', 'work_shift_display'
        ]
