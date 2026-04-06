"""
Models Layer - Hóa đơn và Chi tiết đơn hàng
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from api.customers.models import KhachHang
from api.products.models import SanPham


class HoaDon(models.Model):
    """Model cho hóa đơn (Order)"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xác nhận'),
        ('PREPARING', 'Đang chuẩn bị'),
        ('COMPLETED', 'Hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Tiền mặt'),
        ('CARD', 'Thẻ'),
        ('MOMO', 'MoMo'),
        ('BANKING', 'Chuyển khoản'),
    ]
    
    OrderID = models.AutoField(primary_key=True)
    CustomerID = models.ForeignKey(
        KhachHang,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Khách hàng'
    )
    EmployeeID = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Nhân viên',
        related_name='orders'
    )
    OrderDate = models.DateTimeField(
        default=timezone.now,
        verbose_name='Ngày đặt',
        db_index=True  # Index cho queries thống kê theo thời gian
    )
    TotalAmount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Tổng tiền'
    )
    Discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Giảm giá'
    )
    FinalAmount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Thành tiền'
    )
    PaymentMethod = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='CASH',
        verbose_name='Phương thức thanh toán',
        db_index=True  # Index cho filter theo phương thức
    )
    Status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='Trạng thái',
        db_index=True  # Index cho filter theo trạng thái
    )
    
    class Meta:
        db_table = 'HoaDon'
        verbose_name = 'Hóa đơn'
        verbose_name_plural = 'Hóa đơn'
        ordering = ['-OrderDate']
        indexes = [
            # Compound indexes cho queries phức tạp
            models.Index(fields=['OrderDate', 'Status'], name='idx_order_date_status'),
            models.Index(fields=['Status', 'OrderDate'], name='idx_status_date'),
            models.Index(fields=['CustomerID', 'OrderDate'], name='idx_customer_date'),
            models.Index(fields=['EmployeeID', 'OrderDate'], name='idx_employee_date'),
            models.Index(fields=['PaymentMethod'], name='idx_payment_method'),
        ]
    
    def __str__(self):
        return f"HD{self.OrderID} - {self.OrderDate.strftime('%d/%m/%Y')}"
    
    def calculate_total(self):
        """Tính tổng tiền từ chi tiết đơn hàng"""
        total = sum(detail.Subtotal for detail in self.chitietdonhang_set.all())
        return total
    
    def calculate_final_amount(self):
        """Tính thành tiền sau giảm giá"""
        return max(0, self.TotalAmount - self.Discount)


class ChiTietDonHang(models.Model):
    """Model cho chi tiết đơn hàng (Order Detail)"""
    OrderDetailID = models.AutoField(primary_key=True)
    OrderID = models.ForeignKey(
        HoaDon,
        on_delete=models.CASCADE,
        verbose_name='Hóa đơn'
    )
    ProductID = models.ForeignKey(
        SanPham,
        on_delete=models.PROTECT,
        verbose_name='Sản phẩm'
    )
    Quantity = models.IntegerField(verbose_name='Số lượng')
    UnitPrice = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Đơn giá'
    )
    Subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Thành tiền'
    )
    ToppingNote = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ghi chú topping'
    )
    
    class Meta:
        db_table = 'ChiTietDonHang'
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'
        indexes = [
            models.Index(fields=['OrderID']),
            models.Index(fields=['ProductID']),
        ]
    
    def __str__(self):
        return f"{self.OrderID} - {self.ProductID.ProductName}"
    
    def save(self, *args, **kwargs):
        """Override save để tự động tính Subtotal"""
        self.Subtotal = self.Quantity * self.UnitPrice
        super().save(*args, **kwargs)
