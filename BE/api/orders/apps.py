from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.orders'
    verbose_name = 'Đơn hàng'
    
    def ready(self):
        import api.orders.signals
