"""
Signals cho Inventory app
Phase 4: Added low stock alerts
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ChiTietNhapKho
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ChiTietNhapKho)
def update_import_total_on_detail_save(sender, instance, created, **kwargs):
    """
    Tự động cập nhật tổng tiền của phiếu nhập kho khi chi tiết thay đổi
    """
    import_receipt = instance.ImportID
    import_receipt.TotalAmount = import_receipt.calculate_total()
    import_receipt.save()


@receiver(post_delete, sender=ChiTietNhapKho)
def update_import_total_on_detail_delete(sender, instance, **kwargs):
    """
    Tự động cập nhật tổng tiền của phiếu nhập kho khi xóa chi tiết
    """
    import_receipt = instance.ImportID
    import_receipt.TotalAmount = import_receipt.calculate_total()
    import_receipt.save()


# Phase 4: Low stock monitoring
@receiver(post_save, sender=ChiTietNhapKho)
def check_low_stock_on_import(sender, instance, **kwargs):
    """
    Kiểm tra hàng tồn kho sau khi nhập hàng
    Gửi alert nếu tồn kho thấp
    """
    try:
        from api.ingredients.models import NguyenLieu
        from api.realtime.notifications import send_low_stock_alert
        
        ingredient = instance.IngredientID
        
        # Kiểm tra nếu có MinQuantity được set
        if hasattr(ingredient, 'MinQuantity') and ingredient.MinQuantity:
            current_qty = ingredient.Quantity
            min_qty = ingredient.MinQuantity
            
            # Gửi alert nếu tồn kho < 150% min_quantity
            if current_qty < min_qty * 1.5:
                send_low_stock_alert(
                    ingredient_name=ingredient.IngredientName,
                    current_quantity=current_qty,
                    min_quantity=min_qty,
                    ingredient_id=ingredient.IngredientID
                )
                logger.warning(f"Low stock detected: {ingredient.IngredientName}")
                
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Error checking low stock: {e}")
