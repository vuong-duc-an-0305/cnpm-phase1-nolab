"""
Serializers Layer - Công thức
"""
from rest_framework import serializers
from .models import CongThuc
from api.products.serializers import SanPhamSerializer
from api.ingredients.serializers import NguyenLieuSerializer


class CongThucSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho công thức"""
    
    class Meta:
        model = CongThuc
        fields = ['ProductID', 'IngredientID', 'Quantity', 'Unit']
    
    def validate_Quantity(self, value):
        """Validate số lượng phải lớn hơn 0"""
        if value <= 0:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        return value
    
    def validate(self, attrs):
        """Validate toàn bộ dữ liệu"""
        # Kiểm tra công thức đã tồn tại chưa (khi tạo mới)
        if not self.instance:
            product_id = attrs.get('ProductID')
            ingredient_id = attrs.get('IngredientID')
            
            if CongThuc.objects.filter(
                ProductID=product_id,
                IngredientID=ingredient_id
            ).exists():
                raise serializers.ValidationError(
                    "Công thức cho sản phẩm và nguyên liệu này đã tồn tại"
                )
        
        return attrs


class CongThucDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho công thức (có thông tin sản phẩm và nguyên liệu)"""
    product = SanPhamSerializer(source='ProductID', read_only=True)
    ingredient = NguyenLieuSerializer(source='IngredientID', read_only=True)
    
    class Meta:
        model = CongThuc
        fields = ['ProductID', 'product', 'IngredientID', 'ingredient', 'Quantity', 'Unit']


class CongThucListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách công thức (tối ưu performance)"""
    product_name = serializers.CharField(source='ProductID.ProductName', read_only=True)
    ingredient_name = serializers.CharField(source='IngredientID.IngredientName', read_only=True)
    ingredient_stock = serializers.DecimalField(
        source='IngredientID.QuantityInStock',
        max_digits=12,
        decimal_places=3,
        read_only=True
    )
    ingredient_unit = serializers.CharField(source='IngredientID.Unit', read_only=True)
    
    class Meta:
        model = CongThuc
        fields = [
            'ProductID', 'product_name',
            'IngredientID', 'ingredient_name', 'ingredient_stock', 'ingredient_unit',
            'Quantity', 'Unit'
        ]


class CongThucCreateSerializer(serializers.Serializer):
    """Serializer cho việc tạo công thức hàng loạt"""
    ProductID = serializers.IntegerField()
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        help_text="Danh sách nguyên liệu [{IngredientID, Quantity, Unit}]"
    )
    
    def validate_ingredients(self, value):
        """Validate danh sách nguyên liệu"""
        if not value:
            raise serializers.ValidationError("Danh sách nguyên liệu không được trống")
        
        for item in value:
            if 'IngredientID' not in item:
                raise serializers.ValidationError("Thiếu IngredientID")
            if 'Quantity' not in item:
                raise serializers.ValidationError("Thiếu Quantity")
            if 'Unit' not in item:
                raise serializers.ValidationError("Thiếu Unit")
            
            try:
                quantity = float(item['Quantity'])
                if quantity <= 0:
                    raise serializers.ValidationError("Quantity phải lớn hơn 0")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Quantity không hợp lệ")
        
        return value
