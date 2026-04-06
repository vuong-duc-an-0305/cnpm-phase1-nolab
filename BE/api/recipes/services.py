"""
Service Layer - Business Logic cho Công thức
"""
from django.db import transaction
from django.db.models import Prefetch
from .models import CongThuc
from api.products.models import SanPham
from api.ingredients.models import NguyenLieu


class RecipeService:
    """Service xử lý business logic cho công thức"""
    
    @staticmethod
    def get_all_recipes(product_id=None, ingredient_id=None):
        """
        Lấy danh sách công thức với filter
        
        Args:
            product_id: Lọc theo sản phẩm
            ingredient_id: Lọc theo nguyên liệu
        """
        queryset = CongThuc.objects.select_related(
            'ProductID',
            'IngredientID'
        ).all()
        
        if product_id:
            queryset = queryset.filter(ProductID=product_id)
        
        if ingredient_id:
            queryset = queryset.filter(IngredientID=ingredient_id)
        
        return queryset.order_by('ProductID__ProductName', 'IngredientID__IngredientName')
    
    @staticmethod
    def get_recipe_by_product_and_ingredient(product_id, ingredient_id):
        """Lấy công thức theo sản phẩm và nguyên liệu"""
        try:
            return CongThuc.objects.select_related(
                'ProductID',
                'IngredientID'
            ).get(
                ProductID=product_id,
                IngredientID=ingredient_id
            )
        except CongThuc.DoesNotExist:
            return None
    
    @staticmethod
    def get_recipes_by_product(product_id):
        """Lấy tất cả công thức của một sản phẩm"""
        return CongThuc.objects.filter(
            ProductID=product_id
        ).select_related('IngredientID')
    
    @staticmethod
    def get_products_using_ingredient(ingredient_id):
        """Lấy danh sách sản phẩm sử dụng nguyên liệu"""
        return CongThuc.objects.filter(
            IngredientID=ingredient_id
        ).select_related('ProductID')
    
    @staticmethod
    def create_recipe(recipe_data):
        """Tạo công thức mới"""
        recipe = CongThuc.objects.create(**recipe_data)
        return recipe
    
    @staticmethod
    @transaction.atomic
    def create_recipes_bulk(product_id, ingredients_list):
        """
        Tạo nhiều công thức cho một sản phẩm
        
        Args:
            product_id: ID sản phẩm
            ingredients_list: List of dict [{IngredientID, Quantity, Unit}]
        
        Returns:
            (success, message, recipes)
        """
        # Kiểm tra sản phẩm tồn tại
        try:
            product = SanPham.objects.get(ProductID=product_id)
        except SanPham.DoesNotExist:
            return False, "Sản phẩm không tồn tại", []
        
        # Xóa công thức cũ nếu có
        CongThuc.objects.filter(ProductID=product_id).delete()
        
        # Tạo công thức mới
        recipes = []
        for item in ingredients_list:
            try:
                ingredient = NguyenLieu.objects.get(IngredientID=item['IngredientID'])
                recipe = CongThuc.objects.create(
                    ProductID=product,
                    IngredientID=ingredient,
                    Quantity=item['Quantity'],
                    Unit=item['Unit']
                )
                recipes.append(recipe)
            except NguyenLieu.DoesNotExist:
                transaction.set_rollback(True)
                return False, f"Nguyên liệu ID {item['IngredientID']} không tồn tại", []
        
        return True, "Tạo công thức thành công", recipes
    
    @staticmethod
    def update_recipe(product_id, ingredient_id, recipe_data):
        """Cập nhật công thức"""
        recipe = RecipeService.get_recipe_by_product_and_ingredient(product_id, ingredient_id)
        if recipe:
            for key, value in recipe_data.items():
                if key not in ['ProductID', 'IngredientID']:  # Không cho phép thay đổi ID
                    setattr(recipe, key, value)
            recipe.save()
        return recipe
    
    @staticmethod
    def delete_recipe(product_id, ingredient_id):
        """Xóa công thức"""
        recipe = RecipeService.get_recipe_by_product_and_ingredient(product_id, ingredient_id)
        if recipe:
            recipe.delete()
            return True, "Xóa công thức thành công"
        return False, "Không tìm thấy công thức"
    
    @staticmethod
    def delete_recipes_by_product(product_id):
        """Xóa tất cả công thức của một sản phẩm"""
        deleted_count, _ = CongThuc.objects.filter(ProductID=product_id).delete()
        return deleted_count
    
    @staticmethod
    def check_recipe_completeness(product_id):
        """
        Kiểm tra sản phẩm có đủ công thức không
        
        Returns:
            (has_recipe, recipe_count, ingredients_list)
        """
        recipes = RecipeService.get_recipes_by_product(product_id)
        recipe_count = recipes.count()
        
        ingredients_list = [
            {
                'ingredient_id': r.IngredientID.IngredientID,
                'ingredient_name': r.IngredientID.IngredientName,
                'quantity': r.Quantity,
                'unit': r.Unit,
                'stock': r.IngredientID.QuantityInStock
            }
            for r in recipes
        ]
        
        return recipe_count > 0, recipe_count, ingredients_list
