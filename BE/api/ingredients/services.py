"""
Service Layer - Business Logic cho Nguyên liệu
"""
from django.db.models import Q, F
from .models import NguyenLieu


class IngredientService:
    """Service xử lý business logic cho nguyên liệu"""
    
    @staticmethod
    def get_all_ingredients(search=None):
        """Lấy danh sách nguyên liệu với tìm kiếm"""
        queryset = NguyenLieu.objects.all()
        
        if search:
            queryset = queryset.filter(IngredientName__icontains=search)
        
        return queryset.order_by('IngredientName')
    
    @staticmethod
    def get_ingredient_by_id(ingredient_id):
        """Lấy nguyên liệu theo ID"""
        try:
            return NguyenLieu.objects.get(IngredientID=ingredient_id)
        except NguyenLieu.DoesNotExist:
            return None
    
    @staticmethod
    def get_low_stock_ingredients():
        """Lấy danh sách nguyên liệu sắp hết (dưới mức tối thiểu)"""
        return NguyenLieu.objects.filter(
            QuantityInStock__lte=F('MinQuantity')
        ).order_by('QuantityInStock')
    
    @staticmethod
    def create_ingredient(ingredient_data):
        """Tạo nguyên liệu mới"""
        ingredient = NguyenLieu.objects.create(**ingredient_data)
        return ingredient
    
    @staticmethod
    def update_ingredient(ingredient_id, ingredient_data):
        """Cập nhật nguyên liệu"""
        ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
        if ingredient:
            for key, value in ingredient_data.items():
                setattr(ingredient, key, value)
            ingredient.save()
        return ingredient
    
    @staticmethod
    def delete_ingredient(ingredient_id):
        """Xóa nguyên liệu"""
        ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
        if ingredient:
            # Kiểm tra xem có công thức nào sử dụng nguyên liệu này không
            if ingredient.congthuc_set.exists():
                return False, "Không thể xóa nguyên liệu đang được sử dụng trong công thức"
            
            # Kiểm tra xem có phiếu nhập kho nào sử dụng nguyên liệu này không
            if ingredient.chitietnhapkho_set.exists():
                return False, "Không thể xóa nguyên liệu đã có lịch sử nhập kho"
            
            ingredient.delete()
            return True, "Xóa thành công"
        return False, "Không tìm thấy nguyên liệu"
    
    @staticmethod
    def update_stock(ingredient_id, quantity, is_add=True):
        """
        Cập nhật số lượng tồn kho
        
        Args:
            ingredient_id: ID nguyên liệu
            quantity: Số lượng cần thêm/trừ
            is_add: True = cộng, False = trừ
        
        Returns:
            (success, message, ingredient)
        """
        ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
        if not ingredient:
            return False, "Không tìm thấy nguyên liệu", None
        
        if is_add:
            ingredient.QuantityInStock += quantity
        else:
            if ingredient.QuantityInStock < quantity:
                return False, "Số lượng tồn kho không đủ", None
            ingredient.QuantityInStock -= quantity
        
        ingredient.save()
        return True, "Cập nhật thành công", ingredient
    
    @staticmethod
    def check_stock_availability(ingredient_id, required_quantity):
        """Kiểm tra nguyên liệu có đủ không"""
        ingredient = IngredientService.get_ingredient_by_id(ingredient_id)
        if not ingredient:
            return False, "Không tìm thấy nguyên liệu"
        
        if ingredient.QuantityInStock < required_quantity:
            return False, f"Không đủ {ingredient.IngredientName}. Cần: {required_quantity}, Có: {ingredient.QuantityInStock}"
        
        return True, "Đủ nguyên liệu"
