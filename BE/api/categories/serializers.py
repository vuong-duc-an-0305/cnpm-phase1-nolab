"""
Serializers Layer - Danh mục sản phẩm
"""
from rest_framework import serializers
from .models import DanhMucSanPham


class DanhMucSanPhamSerializer(serializers.ModelSerializer):
    """Serializer cho danh mục sản phẩm"""
    
    class Meta:
        model = DanhMucSanPham
        fields = ['CategoryID', 'CategoryName']
        read_only_fields = ['CategoryID']
    
    def validate_CategoryName(self, value):
        """Validate tên danh mục không được trùng"""
        if not value or not value.strip():
            raise serializers.ValidationError("Tên danh mục không được để trống")
        
        # Kiểm tra trùng tên (trừ chính nó khi update)
        queryset = DanhMucSanPham.objects.filter(CategoryName=value)
        if self.instance:
            queryset = queryset.exclude(CategoryID=self.instance.CategoryID)
        
        if queryset.exists():
            raise serializers.ValidationError("Tên danh mục đã tồn tại")
        
        return value.strip()


class DanhMucSanPhamListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách danh mục (có thêm số lượng sản phẩm)"""
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DanhMucSanPham
        fields = ['CategoryID', 'CategoryName', 'product_count']
