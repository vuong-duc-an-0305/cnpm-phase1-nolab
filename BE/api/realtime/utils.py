"""
Utility functions để broadcast messages qua WebSocket
Phase 2: Helper functions cho real-time updates
"""
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def broadcast_dashboard_update(stats_data):
    """
    Broadcast cập nhật thống kê đến tất cả dashboard clients
    
    Args:
        stats_data: Dict chứa statistics data
        
    Example:
        broadcast_dashboard_update({
            'total_orders': 150,
            'total_revenue': 15000000,
            'avg_order_value': 100000
        })
    """
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        logger.warning("Channel layer not configured")
        return
    
    try:
        async_to_sync(channel_layer.group_send)(
            'dashboard',
            {
                'type': 'stats_update',
                'data': stats_data
            }
        )
        logger.info("Dashboard stats broadcasted successfully")
    except Exception as e:
        logger.error(f"Failed to broadcast dashboard update: {e}")


def broadcast_order_created(order_data):
    """
    Broadcast thông báo đơn hàng mới
    
    Args:
        order_data: Dict chứa order information
        
    Example:
        broadcast_order_created({
            'order_id': 123,
            'customer_name': 'Nguyen Van A',
            'total_amount': 150000,
            'items_count': 3
        })
    """
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        return
    
    try:
        async_to_sync(channel_layer.group_send)(
            'dashboard',
            {
                'type': 'order_created',
                'data': order_data
            }
        )
        logger.info(f"Order created notification sent: Order #{order_data.get('order_id')}")
    except Exception as e:
        logger.error(f"Failed to broadcast order created: {e}")


def broadcast_order_updated(order_data):
    """
    Broadcast thông báo cập nhật trạng thái đơn hàng
    
    Args:
        order_data: Dict chứa order update info
        
    Example:
        broadcast_order_updated({
            'order_id': 123,
            'old_status': 'PENDING',
            'new_status': 'COMPLETED'
        })
    """
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        return
    
    try:
        async_to_sync(channel_layer.group_send)(
            'dashboard',
            {
                'type': 'order_updated',
                'data': order_data
            }
        )
        logger.info(f"Order updated notification sent: Order #{order_data.get('order_id')}")
    except Exception as e:
        logger.error(f"Failed to broadcast order updated: {e}")


def broadcast_attendance_checkin(attendance_data):
    """
    Broadcast thông báo nhân viên chấm công
    
    Args:
        attendance_data: Dict chứa attendance info
        
    Example:
        broadcast_attendance_checkin({
            'employee_name': 'Nguyen Van A',
            'check_in_time': '08:00:00',
            'type': 'check_in'
        })
    """
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        return
    
    try:
        async_to_sync(channel_layer.group_send)(
            'dashboard',
            {
                'type': 'attendance_checkin',
                'data': attendance_data
            }
        )
        logger.info(f"Attendance check-in notification sent for {attendance_data.get('employee_name')}")
    except Exception as e:
        logger.error(f"Failed to broadcast attendance check-in: {e}")


def send_user_notification(user_id, notification_data):
    """
    Gửi notification đến một user cụ thể
    
    Args:
        user_id: ID của user
        notification_data: Dict chứa notification data
        
    Example:
        send_user_notification(user_id=5, notification_data={
            'title': 'New Order',
            'message': 'You have a new order #123',
            'level': 'info'
        })
    """
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        return
    
    try:
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'notification',
                'data': notification_data
            }
        )
        logger.info(f"Notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")
