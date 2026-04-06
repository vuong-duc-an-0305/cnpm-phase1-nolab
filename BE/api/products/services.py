"""
Service Layer - Business Logic cho Sản phẩm
"""
from django.db.models import Q, Prefetch
from .models import SanPham


class ProductService:
    """Service xử lý business logic cho sản phẩm"""
    
    @staticmethod
    def get_all_products(category_id=None, status=None, search=None):
        """
        Lấy danh sách sản phẩm với các filter
        
        Args:
            category_id: Lọc theo danh mục
            status: Lọc theo trạng thái
            search: Tìm kiếm theo tên
        """
        queryset = SanPham.objects.select_related('CategoryID').all()
        
        if category_id:
            queryset = queryset.filter(CategoryID=category_id)
        
        if status is not None:
            queryset = queryset.filter(Status=status)
        
        if search:
            queryset = queryset.filter(
                Q(ProductName__icontains=search) |
                Q(CategoryID__CategoryName__icontains=search)
            )
        
        return queryset.order_by('ProductName')
    
    @staticmethod
    def get_product_by_id(product_id):
        """Lấy sản phẩm theo ID"""
        try:
            return SanPham.objects.select_related('CategoryID').get(ProductID=product_id)
        except SanPham.DoesNotExist:
            return None
    
    @staticmethod
    def get_available_products():
        """Lấy danh sách sản phẩm còn hàng"""
        return SanPham.objects.filter(Status=1).select_related('CategoryID')
    
    @staticmethod
    def create_product(product_data):
        """Tạo sản phẩm mới"""
        product = SanPham.objects.create(**product_data)
        return product
    
    @staticmethod
    def update_product(product_id, product_data):
        """Cập nhật sản phẩm"""
        product = ProductService.get_product_by_id(product_id)
        if product:
            for key, value in product_data.items():
                setattr(product, key, value)
            product.save()
        return product
    
    @staticmethod
    def delete_product(product_id):
        """Xóa sản phẩm"""
        product = ProductService.get_product_by_id(product_id)
        if product:
            # Kiểm tra xem có đơn hàng nào sử dụng sản phẩm này không
            if product.chitietdonhang_set.exists():
                return False, "Không thể xóa sản phẩm đã có trong đơn hàng"
            
            # Kiểm tra xem có công thức nào sử dụng sản phẩm này không
            if product.congthuc_set.exists():
                return False, "Không thể xóa sản phẩm đang có công thức"
            
            product.delete()
            return True, "Xóa thành công"
        return False, "Không tìm thấy sản phẩm"
    
    @staticmethod
    def update_product_status(product_id, status):
        """Cập nhật trạng thái sản phẩm"""
        product = ProductService.get_product_by_id(product_id)
        if product:
            product.Status = status
            product.save()
            return True, product
        return False, None
    
    @staticmethod
    def get_products_by_category(category_id):
        """Lấy sản phẩm theo danh mục"""
        return SanPham.objects.filter(CategoryID=category_id).select_related('CategoryID')
    
    @staticmethod
    def check_ingredients_availability(product_id, quantity=1):
        """
        Kiểm tra nguyên liệu có đủ để làm sản phẩm không
        
        Returns:
            (bool, list): (có đủ nguyên liệu, danh sách nguyên liệu thiếu)
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return False, ["Sản phẩm không tồn tại"]
        
        # Lấy công thức của sản phẩm
        recipes = product.congthuc_set.select_related('IngredientID').all()
        
        missing_ingredients = []
        for recipe in recipes:
            required_quantity = recipe.Quantity * quantity
            if recipe.IngredientID.QuantityInStock < required_quantity:
                missing_ingredients.append({
                    'ingredient': recipe.IngredientID.IngredientName,
                    'required': required_quantity,
                    'available': recipe.IngredientID.QuantityInStock,
                    'unit': recipe.Unit
                })
        
        if missing_ingredients:
            return False, missing_ingredients
        
        return True, []
