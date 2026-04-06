"""
Real-time Notification Helpers
Phase 4: Toast notifications, alerts, summaries
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def send_toast_notification(message, notification_type='info', title=None, duration=5000):
    """
    Gửi toast notification đến tất cả dashboard clients
    
    Args:
        message: Nội dung thông báo
        notification_type: 'success', 'error', 'warning', 'info'
        title: Tiêu đề (optional)
        duration: Thời gian hiển thị (ms), default 5000
    """
    channel_layer = get_channel_layer()
    
    data = {
        'message': message,
        'type_name': notification_type,
        'title': title or notification_type.capitalize(),
        'duration': duration,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        async_to_sync(channel_layer.group_send)(
            'dashboard',
            {
                'type': 'toast_notification',
                'data': data
            }
        )
        logger.info(f"Toast notification sent: {notification_type} - {message}")
    except Exception as e:
        logger.error(f"Failed to send toast notification: {e}")


def send_low_stock_alert(ingredient_name, current_quantity, min_quantity, ingredient_id):
    """
    Gửi cảnh báo hàng tồn kho thấp
    
    Args:
        ingredient_name: Tên nguyên liệu
        current_quantity: Số lượng hiện tại
        min_quantity: Số lượng tối thiểu
        ingredient_id: ID nguyên liệu
    """
    channel_layer = get_channel_layer()
    
    data = {
        'ingredient_id': ingredient_id,
        'ingredient_name': ingredient_name,
        'current_quantity': float(current_quantity),
        'min_quantity': float(min_quantity),
        'alert_level': 'critical' if current_quantity < min_quantity * 0.5 else 'warning',
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        async_to_sync(channel_layer.group_send)(
            'dashboard',
            {
                'type': 'low_stock_alert',
                'data': data
            }
        )
        logger.warning(f"Low stock alert: {ingredient_name} ({current_quantity}/{min_quantity})")
        
        # Also send as toast
        send_toast_notification(
            f"Cảnh báo: {ingredient_name} còn {current_quantity} (tối thiểu: {min_quantity})",
            notification_type='warning',
            title='Hàng tồn kho thấp'
        )
    except Exception as e:
        logger.error(f"Failed to send low stock alert: {e}")


def send_daily_summary(date, total_orders, total_revenue, top_products=None):
    """
    Gửi tổng kết cuối ngày
    
    Args:
        date: Ngày tổng kết (datetime.date)
        total_orders: Tổng số đơn hàng
        total_revenue: Tổng doanh thu
        top_products: List top sản phẩm bán chạy (optional)
    """
    channel_layer = get_channel_layer()
    
    data = {
        'date': date.isoformat(),
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'top_products': top_products or [],
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        async_to_sync(channel_layer.group_send)(
            'dashboard',
            {
                'type': 'daily_summary',
                'data': data
            }
        )
        logger.info(f"Daily summary sent: {date} - {total_orders} orders, {total_revenue} VND")
        
        # Also send as toast
        send_toast_notification(
            f"Tổng kết {date}: {total_orders} đơn hàng, {total_revenue:,.0f} VND",
            notification_type='info',
            title='Tổng kết cuối ngày',
            duration=10000
        )
    except Exception as e:
        logger.error(f"Failed to send daily summary: {e}")


def get_online_users_count():
    """
    Lấy số lượng users đang online
    """
    from api.realtime.consumers import ONLINE_USERS
    return len(ONLINE_USERS)
