"""
Serializers Layer - Nguyên liệu
"""
from rest_framework import serializers
from .models import NguyenLieu


class NguyenLieuSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho nguyên liệu"""
    
    class Meta:
        model = NguyenLieu
        fields = [
            'IngredientID', 'IngredientName', 'Unit', 'QuantityInStock', 'MinQuantity'
        ]
        read_only_fields = ['IngredientID']
    
    def validate_QuantityInStock(self, value):
        """Validate số lượng tồn kho không âm"""
        if value < 0:
            raise serializers.ValidationError("Số lượng tồn kho không được âm")
        return value
    
    def validate_MinQuantity(self, value):
        """Validate số lượng tối thiểu không âm"""
        if value < 0:
            raise serializers.ValidationError("Số lượng tối thiểu không được âm")
        return value
    
    def validate_IngredientName(self, value):
        """Validate tên nguyên liệu"""
        if not value or not value.strip():
            raise serializers.ValidationError("Tên nguyên liệu không được để trống")
        return value.strip()


class NguyenLieuDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho nguyên liệu"""
    is_low_stock = serializers.BooleanField(read_only=True)
    stock_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = NguyenLieu
        fields = [
            'IngredientID', 'IngredientName', 'Unit', 'QuantityInStock',
            'MinQuantity', 'is_low_stock', 'stock_percentage'
        ]
        read_only_fields = ['IngredientID']


class NguyenLieuStockUpdateSerializer(serializers.Serializer):
    """Serializer cho việc cập nhật số lượng tồn kho"""
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=3,
        required=True,
        help_text="Số lượng cần thêm (số dương) hoặc trừ (số âm)"
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Ghi chú"
    )
