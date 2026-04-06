"""
Serializers Layer - Sản phẩm
"""
from rest_framework import serializers
from .models import SanPham
from api.categories.serializers import DanhMucSanPhamSerializer
from api.recipes.models import CongThuc


class SanPhamSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho sản phẩm"""
    
    class Meta:
        model = SanPham
        fields = [
            'ProductID', 'ProductName', 'Price', 'ImageUrl',
            'CategoryID', 'Status'
        ]
        read_only_fields = ['ProductID']
    
    def validate_Price(self, value):
        """Validate giá phải lớn hơn 0"""
        if value <= 0:
            raise serializers.ValidationError("Giá sản phẩm phải lớn hơn 0")
        return value
    
    def validate_ProductName(self, value):
        """Validate tên sản phẩm"""
        if not value or not value.strip():
            raise serializers.ValidationError("Tên sản phẩm không được để trống")
        return value.strip()


class SanPhamDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho sản phẩm (có thông tin danh mục)"""
    category = DanhMucSanPhamSerializer(source='CategoryID', read_only=True)
    status_display = serializers.CharField(source='get_Status_display', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    ingredients = serializers.SerializerMethodField()
    
    class Meta:
        model = SanPham
        fields = [
            'ProductID', 'ProductName', 'Price', 'ImageUrl',
            'CategoryID', 'category', 'Status', 'status_display', 'is_available',
            'ingredients'
        ]
        read_only_fields = ['ProductID']

    def get_ingredients(self, obj):
        recipes = CongThuc.objects.filter(ProductID=obj).select_related('IngredientID')
        result = []
        for r in recipes:
            result.append({
                'IngredientID': r.IngredientID.IngredientID,
                'IngredientName': r.IngredientID.IngredientName,
                'IngredientUnit': r.IngredientID.Unit,
                'Quantity': r.Quantity,
                'Unit': r.Unit,
                'QuantityInStock': r.IngredientID.QuantityInStock,
            })
        return result


class SanPhamListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách sản phẩm (tối ưu performance)"""
    category_name = serializers.CharField(source='CategoryID.CategoryName', read_only=True)
    status_display = serializers.CharField(source='get_Status_display', read_only=True)
    
    class Meta:
        model = SanPham
        fields = [
            'ProductID', 'ProductName', 'Price', 'ImageUrl',
            'CategoryID', 'category_name', 'Status', 'status_display'
        ]


class SanPhamCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo/cập nhật sản phẩm"""
    
    class Meta:
        model = SanPham
        fields = [
            'ProductName', 'Price', 'ImageUrl', 'CategoryID', 'Status'
        ]
    
    def validate(self, attrs):
        """Validate toàn bộ dữ liệu"""
        if attrs.get('Price', 0) <= 0:
            raise serializers.ValidationError({'Price': 'Giá sản phẩm phải lớn hơn 0'})
        return attrs
