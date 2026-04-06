"""
Signals cho Orders app
Phase 2: Added real-time broadcasting
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import HoaDon, ChiTietDonHang
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ChiTietDonHang)
def update_order_total_on_detail_save(sender, instance, created, **kwargs):
    """
    Tự động cập nhật tổng tiền của hóa đơn khi chi tiết thay đổi
    """
    order = instance.OrderID
    order.TotalAmount = order.calculate_total()
    order.FinalAmount = order.calculate_final_amount()
    order.save()


@receiver(post_delete, sender=ChiTietDonHang)
def update_order_total_on_detail_delete(sender, instance, **kwargs):
    """
    Tự động cập nhật tổng tiền của hóa đơn khi xóa chi tiết
    """
    order = instance.OrderID
    order.TotalAmount = order.calculate_total()
    order.FinalAmount = order.calculate_final_amount()
    order.save()


# Phase 2: Real-time WebSocket broadcasts

@receiver(post_save, sender=HoaDon)
def broadcast_order_changes(sender, instance, created, **kwargs):
    """
    Broadcast order changes qua WebSocket
    - Khi tạo order mới: broadcast order_created
    - Khi cập nhật order: broadcast order_updated
    """
    try:
        from api.realtime.utils import broadcast_order_created, broadcast_order_updated, broadcast_dashboard_update
        from .services import OrderService
        from datetime import date
        
        # Prepare order data
        order_data = {
            'order_id': instance.OrderID,
            'customer_name': instance.CustomerID.FullName if instance.CustomerID else 'Khách vãng lai',
            'employee_name': instance.EmployeeID.username if instance.EmployeeID else '',
            'total_amount': float(instance.FinalAmount),
            'status': instance.Status,
            'order_date': instance.OrderDate.isoformat() if instance.OrderDate else None,
        }
        
        if created:
            # Đơn hàng mới
            broadcast_order_created(order_data)
            logger.info(f"Broadcasted new order #{instance.OrderID}")
            
            # Phase 4: Send toast notification
            from api.realtime.notifications import send_toast_notification
            send_toast_notification(
                f"Đơn hàng mới #{instance.OrderID} - {instance.CustomerID.FullName if instance.CustomerID else 'Khách vãng lai'}",
                notification_type='success',
                title='Đơn hàng mới'
            )
        else:
            # Cập nhật trạng thái
            broadcast_order_updated(order_data)
            logger.info(f"Broadcasted order update #{instance.OrderID}")
        
        # Cập nhật dashboard stats (chỉ cho hôm nay)
        today = date.today()
        stats = OrderService.get_revenue_statistics(
            from_date=today,
            to_date=today,
            include_all_status=True
        )
        
        # Gửi stats summary đến dashboard
        if stats and 'summary' in stats:
            broadcast_dashboard_update({
                'total_orders': stats['summary']['total_orders'],
                'total_revenue': float(stats['summary']['total_revenue']),
                'average_order_value': float(stats['summary']['average_order_value']),
                'timestamp': today.isoformat()
            })
            logger.info("Broadcasted dashboard stats update")
            
    except ImportError:
        # Nếu realtime module chưa có, skip
        pass
    except Exception as e:
        logger.error(f"Error broadcasting order changes: {e}")
