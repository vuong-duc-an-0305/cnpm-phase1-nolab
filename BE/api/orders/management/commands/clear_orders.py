"""
Script để xóa tất cả dữ liệu hóa đơn cũ
"""
from django.core.management.base import BaseCommand
from api.orders.models import HoaDon, ChiTietDonHang


class Command(BaseCommand):
    help = 'Xóa tất cả dữ liệu hóa đơn cũ'

    def handle(self, *args, **options):
        # Đếm số lượng trước khi xóa
        order_count = HoaDon.objects.count()
        detail_count = ChiTietDonHang.objects.count()
        
        self.stdout.write(f'Tìm thấy {order_count} hóa đơn và {detail_count} chi tiết đơn hàng')
        
        # Xóa chi tiết đơn hàng trước
        deleted_details = ChiTietDonHang.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ Đã xóa {deleted_details[0]} chi tiết đơn hàng'))
        
        # Xóa hóa đơn
        deleted_orders = HoaDon.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ Đã xóa {deleted_orders[0]} hóa đơn'))
        
        self.stdout.write(self.style.SUCCESS('✓ Hoàn thành xóa dữ liệu hóa đơn cũ'))
