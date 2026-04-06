"""
Service Layer - Business Logic cho Phiếu nhập kho
"""
from django.db import transaction
from django.db.models import Count, Sum, Avg, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from .models import PhieuNhapKho, ChiTietNhapKho
from api.ingredients.models import NguyenLieu


class InventoryService:
    """Service xử lý business logic cho phiếu nhập kho"""
    
    @staticmethod
    def get_all_imports(employee_id=None, from_date=None, to_date=None):
        """
        Lấy danh sách phiếu nhập kho với filter
        """
        queryset = PhieuNhapKho.objects.select_related('EmployeeID').annotate(
            items_count=Count('chitietnhapkho')
        )
        
        if employee_id:
            queryset = queryset.filter(EmployeeID=employee_id)
        
        if from_date:
            queryset = queryset.filter(ImportDate__gte=from_date)
        
        if to_date:
            queryset = queryset.filter(ImportDate__lt=to_date + timedelta(days=1))
        
        return queryset.order_by('-ImportDate')
    
    @staticmethod
    def get_import_by_id(import_id):
        """Lấy phiếu nhập kho theo ID"""
        try:
            return PhieuNhapKho.objects.select_related('EmployeeID').prefetch_related(
                'chitietnhapkho_set__IngredientID'
            ).annotate(
                items_count=Count('chitietnhapkho')
            ).get(ImportID=import_id)
        except PhieuNhapKho.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def create_import(import_data, items_data):
        """
        Tạo phiếu nhập kho mới với chi tiết
        
        Args:
            import_data: Dict chứa thông tin phiếu nhập
            items_data: List of dict chứa thông tin nguyên liệu
        
        Returns:
            (success, message/import_receipt, errors)
        """
        # Kiểm tra nhân viên
        try:
            employee = NhanVien.objects.get(EmployeeID=import_data['EmployeeID'])
        except NhanVien.DoesNotExist:
            return False, "Nhân viên không tồn tại", []
        
        # Kiểm tra nguyên liệu và tính toán
        import_details = []
        total_amount = 0
        errors = []
        
        for item in items_data:
            try:
                ingredient = NguyenLieu.objects.get(IngredientID=item['IngredientID'])
                
                quantity = item['Quantity']
                unit_price = item['UnitPrice']
                subtotal = quantity * unit_price
                total_amount += subtotal
                
                import_details.append({
                    'ingredient': ingredient,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': subtotal
                })
                
            except NguyenLieu.DoesNotExist:
                errors.append(f"Nguyên liệu ID {item['IngredientID']} không tồn tại")
        
        if errors:
            return False, "Có lỗi khi tạo phiếu nhập kho", errors
        
        if not import_details:
            return False, "Không có nguyên liệu hợp lệ trong phiếu nhập", []
        
        # Tạo phiếu nhập kho
        import_receipt = PhieuNhapKho.objects.create(
            EmployeeID=employee,
            TotalAmount=total_amount
        )
        
        # Tạo chi tiết nhập kho và cập nhật tồn kho
        for detail in import_details:
            ChiTietNhapKho.objects.create(
                ImportID=import_receipt,
                IngredientID=detail['ingredient'],
                Quantity=detail['quantity'],
                UnitPrice=detail['unit_price']
            )
            
            # Cộng vào tồn kho
            detail['ingredient'].QuantityInStock += detail['quantity']
            detail['ingredient'].save()
        
        return True, import_receipt, []
    
    @staticmethod
    @transaction.atomic
    def delete_import(import_id):
        """
        Xóa phiếu nhập kho và trừ nguyên liệu đã nhập
        """
        import_receipt = InventoryService.get_import_by_id(import_id)
        if not import_receipt:
            return False, "Không tìm thấy phiếu nhập kho"
        
        # Trừ nguyên liệu đã nhập
        for detail in import_receipt.chitietnhapkho_set.all():
            ingredient = detail.IngredientID
            
            # Kiểm tra xem có đủ số lượng để trừ không
            if ingredient.QuantityInStock < detail.Quantity:
                return False, f"Không thể xóa phiếu nhập vì nguyên liệu '{ingredient.IngredientName}' đã được sử dụng"
            
            ingredient.QuantityInStock -= detail.Quantity
            ingredient.save()
        
        import_receipt.delete()
        return True, "Xóa phiếu nhập kho thành công"
    
    @staticmethod
    def get_import_statistics(from_date=None, to_date=None):
        """Thống kê nhập kho"""
        queryset = PhieuNhapKho.objects.all()
        
        if from_date:
            queryset = queryset.filter(ImportDate__gte=from_date)
        
        if to_date:
            queryset = queryset.filter(ImportDate__lt=to_date + timedelta(days=1))
        
        stats = queryset.aggregate(
            total_imports=Count('ImportID'),
            total_cost=Coalesce(Sum('TotalAmount'), 0),
            average_import_value=Coalesce(Avg('TotalAmount'), 0)
        )
        
        # Thống kê nguyên liệu được nhập nhiều nhất
        ingredient_stats = ChiTietNhapKho.objects.filter(
            ImportID__in=queryset
        ).values(
            'IngredientID',
            'IngredientID__IngredientName'
        ).annotate(
            total_quantity=Sum('Quantity'),
            total_cost=Sum(
                ExpressionWrapper(
                    F('Quantity') * F('UnitPrice'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            ),
            import_count=Count('ImportID', distinct=True)
        ).order_by('-total_quantity')[:10]
        
        return {
            'summary': stats,
            'top_ingredients': list(ingredient_stats)
        }
    
    @staticmethod
    def get_ingredient_import_history(ingredient_id):
        """Lấy lịch sử nhập kho của nguyên liệu"""
        details = ChiTietNhapKho.objects.filter(
            IngredientID=ingredient_id
        ).select_related(
            'ImportID__EmployeeID'
        ).order_by('-ImportID__ImportDate')
        
        return details
