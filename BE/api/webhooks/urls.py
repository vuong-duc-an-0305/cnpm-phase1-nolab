"""
Webhook URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('order_notification/', views.webhook_order_notification, name='webhook_order_notification'),
    path('inventory_alert/', views.webhook_inventory_alert, name='webhook_inventory_alert'),
    path('health/', views.webhook_health_check, name='webhook_health_check'),
]
