"""
Service Layer - Business Logic cho Danh mục sản phẩm
"""
from django.db.models import Count
from .models import DanhMucSanPham


class CategoryService:
    """Service xử lý business logic cho danh mục"""
    
    @staticmethod
    def get_all_categories_with_product_count():
        """Lấy tất cả danh mục kèm số lượng sản phẩm"""
        return DanhMucSanPham.objects.annotate(
            product_count=Count('sanpham')
        ).order_by('CategoryName')
    
    @staticmethod
    def get_category_by_id(category_id):
        """Lấy danh mục theo ID"""
        try:
            return DanhMucSanPham.objects.get(CategoryID=category_id)
        except DanhMucSanPham.DoesNotExist:
            return None
    
    @staticmethod
    def create_category(category_data):
        """Tạo danh mục mới"""
        category = DanhMucSanPham.objects.create(**category_data)
        return category
    
    @staticmethod
    def update_category(category_id, category_data):
        """Cập nhật danh mục"""
        category = CategoryService.get_category_by_id(category_id)
        if category:
            for key, value in category_data.items():
                setattr(category, key, value)
            category.save()
        return category
    
    @staticmethod
    def delete_category(category_id):
        """Xóa danh mục"""
        category = CategoryService.get_category_by_id(category_id)
        if category:
            # Kiểm tra xem có sản phẩm nào thuộc danh mục này không
            if category.sanpham_set.exists():
                return False, "Không thể xóa danh mục đang có sản phẩm"
            category.delete()
            return True, "Xóa thành công"
        return False, "Không tìm thấy danh mục"
