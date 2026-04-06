"""
Webhook system for external integrations
Phase 3: Allow external systems to send notifications/events
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)


def verify_webhook_signature(request, secret_key):
    """
    Verify webhook signature using HMAC-SHA256
    
    Expected header: X-Webhook-Signature
    """
    signature = request.headers.get('X-Webhook-Signature')
    if not signature:
        return False
    
    # Compute expected signature
    body = request.body
    expected_signature = hmac.new(
        secret_key.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@api_view(['POST'])
@permission_classes([AllowAny])  # Public endpoint, but signature verified
def webhook_order_notification(request):
    """
    POST /api/webhooks/order_notification/
    Receive order notifications from external systems (e.g., delivery partners)
    
    Headers:
        X-Webhook-Signature: HMAC-SHA256 signature
    
    Body: {
        "order_id": 123,
        "status": "delivered|cancelled|....",
        "timestamp": "2024-12-12T10:30:00Z",
        "message": "Order delivered successfully",
        "metadata": {...}
    }
    """
    # Verify signature (if secret key configured)
    webhook_secret = getattr(settings, 'WEBHOOK_SECRET_KEY', None)
    if webhook_secret:
        if not verify_webhook_signature(request, webhook_secret):
            logger.warning(f'Invalid webhook signature from IP: {request.META.get("REMOTE_ADDR")}')
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # Parse webhook data
    data = request.data
    order_id = data.get('order_id')
    order_status = data.get('status')
    message = data.get('message', '')
    
    if not order_id:
        return Response(
            {'error': 'order_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Log webhook received
    logger.info(f'Webhook received for order #{order_id}: status={order_status}, message={message}')
    
    # Process webhook (update order status if needed)
    try:
        from api.orders.models import HoaDon
        from api.orders.services import OrderService
        
        order = HoaDon.objects.filter(OrderID=order_id).first()
        if not order:
            logger.warning(f'Order #{order_id} not found for webhook')
            return Response(
                {'error': f'Order #{order_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Map external status to internal status (if different)
        status_mapping = {
            'delivered': 'COMPLETED',
            'cancelled': 'CANCELLED',
            'processing': 'PREPARING',
            'pending': 'PENDING'
        }
        
        internal_status = status_mapping.get(order_status, order_status)
        
        # Update order status
        if internal_status and order.Status != internal_status:
            success, msg, updated_order = OrderService.update_order_status(order_id, internal_status)
            if success:
                logger.info(f'Order #{order_id} status updated to {internal_status} via webhook')
            else:
                logger.error(f'Failed to update order #{order_id}: {msg}')
        
        # Broadcast update via WebSocket (if Phase 2 enabled)
        try:
            from api.realtime.utils import broadcast_order_updated
            broadcast_order_updated({
                'order_id': order_id,
                'status': internal_status,
                'old_status': order.Status,
                'source': 'webhook'
            })
        except ImportError:
            pass
        
        return Response({
            'status': 'success',
            'message': 'Webhook processed',
            'order_id': order_id,
            'updated_status': internal_status
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f'Error processing webhook for order #{order_id}: {str(e)}')
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_inventory_alert(request):
    """
    POST /api/webhooks/inventory_alert/
    Receive inventory alerts from external inventory management systems
    
    Body: {
        "ingredient_id": 123,
        "ingredient_name": "Cà phê hạt",
        "current_stock": 5.0,
        "alert_type": "low_stock|out_of_stock",
        "timestamp": "2024-12-12T10:30:00Z"
    }
    """
    webhook_secret = getattr(settings, 'WEBHOOK_SECRET_KEY', None)
    if webhook_secret:
        if not verify_webhook_signature(request, webhook_secret):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
    
    data = request.data
    ingredient_id = data.get('ingredient_id')
    alert_type = data.get('alert_type')
    
    logger.info(f'Inventory alert webhook: ingredient_id={ingredient_id}, type={alert_type}')
    
    # Could trigger notifications to admins here
    # Or update inventory status
    
    return Response({
        'status': 'success',
        'message': 'Inventory alert received'
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def webhook_health_check(request):
    """
    GET/POST /api/webhooks/health/
    Health check endpoint for webhook integrations
    """
    return Response({
        'status': 'healthy',
        'service': 'Coffee Shop Webhook Service',
        'timestamp': request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    })
