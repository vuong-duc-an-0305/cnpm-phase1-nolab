"""
WebSocket Consumers for Real-time Features
Phase 2: Push updates to dashboard instead of polling
Phase 4: Enhanced with notifications, online users tracking
"""
import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Track online users globally
ONLINE_USERS = set()


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer cho dashboard real-time updates
    
    Channel: dashboard
    Events:
    - stats_update: Cập nhật thống kê doanh thu
    - order_created: Đơn hàng mới được tạo
    - order_updated: Trạng thái đơn hàng thay đổi
    """
    
    async def connect(self):
        """Xử lý khi client connect"""
        # Join dashboard group
        self.room_group_name = 'dashboard'
        
        # Get user info
        user = self.scope.get("user")
        self.user = user
        
        # Check authentication (optional - bỏ comment nếu cần auth)
        # if isinstance(user, AnonymousUser) or not user.is_authenticated:
        #     await self.close()
        #     return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Track user as online
        if not isinstance(user, AnonymousUser) and user.is_authenticated:
            user_id = str(user.id)
            ONLINE_USERS.add(user_id)
            
            # Broadcast user joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'data': {
                        'user_id': user.id,
                        'username': user.username,
                        'online_count': len(ONLINE_USERS),
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
        
        logger.info(f"WebSocket connected: {self.channel_name} | User: {user}")
        
        # Send welcome message with online users count
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to dashboard updates',
            'online_users': len(ONLINE_USERS)
        }))
    
    async def disconnect(self, close_code):
        """Xử lý khi client disconnect"""
        # Remove user from online users
        user = self.user
        if not isinstance(user, AnonymousUser) and user.is_authenticated:
            user_id = str(user.id)
            ONLINE_USERS.discard(user_id)
            
            # Broadcast user left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'data': {
                        'user_id': user.id,
                        'username': user.username,
                        'online_count': len(ONLINE_USERS),
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
        
        # Leave dashboard group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket disconnected: {self.channel_name} (code: {close_code})")
    
    async def receive(self, text_data):
        """Xử lý message từ client (nếu cần)"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Heartbeat
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    # Handlers cho các event types
    
    async def stats_update(self, event):
        """
        Handler cho event 'stats_update'
        Gửi thống kê mới đến client
        """
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': event['data']
        }))
    
    async def order_created(self, event):
        """
        Handler cho event 'order_created'
        Thông báo đơn hàng mới
        """
        await self.send(text_data=json.dumps({
            'type': 'order_created',
            'data': event['data']
        }))
    
    async def order_updated(self, event):
        """
        Handler cho event 'order_updated'
        Thông báo trạng thái đơn hàng thay đổi
        """
        await self.send(text_data=json.dumps({
            'type': 'order_updated',
            'data': event['data']
        }))
    
    async def attendance_checkin(self, event):
        """
        Handler cho event 'attendance_checkin'
        Thông báo nhân viên chấm công
        """
        await self.send(text_data=json.dumps({
            'type': 'attendance_checkin',
            'data': event['data']
        }))
    
    async def user_joined(self, event):
        """
        Handler cho event 'user_joined'
        Thông báo user mới join
        """
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'data': event['data']
        }))
    
    async def user_left(self, event):
        """
        Handler cho event 'user_left'
        Thông báo user rời khỏi
        """
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'data': event['data']
        }))
    
    async def low_stock_alert(self, event):
        """
        Handler cho event 'low_stock_alert'
        Cảnh báo hàng tồn kho thấp
        """
        await self.send(text_data=json.dumps({
            'type': 'low_stock_alert',
            'data': event['data']
        }))
    
    async def daily_summary(self, event):
        """
        Handler cho event 'daily_summary'
        Tổng kết cuối ngày
        """
        await self.send(text_data=json.dumps({
            'type': 'daily_summary',
            'data': event['data']
        }))
    
    async def toast_notification(self, event):
        """
        Handler cho event 'toast_notification'
        Toast notification (success/error/warning/info)
        """
        await self.send(text_data=json.dumps({
            'type': 'toast_notification',
            'data': event['data']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer cho notifications
    Gửi thông báo cá nhân đến từng user
    """
    
    async def connect(self):
        """Xử lý khi client connect"""
        user = self.scope.get("user")
        
        # Kiểm tra authentication
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return
        
        # Join user-specific group
        self.room_group_name = f'user_{user.id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"Notification channel connected for user {user.username}")
    
    async def disconnect(self, close_code):
        """Xử lý khi client disconnect"""
        user = self.scope.get("user")
        if not isinstance(user, AnonymousUser):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"Notification channel disconnected for user {user.username}")
    
    async def notification(self, event):
        """
        Handler cho event 'notification'
        Gửi notification đến user
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))
