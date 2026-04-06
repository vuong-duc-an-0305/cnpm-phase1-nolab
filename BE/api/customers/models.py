"""
Models Layer - Khách hàng
"""
from django.db import models
from django.utils import timezone


class KhachHang(models.Model):
    """Model cho khách hàng (Customer)"""
    CustomerID = models.AutoField(primary_key=True)
    FullName = models.CharField(max_length=150, verbose_name='Họ tên')
    PhoneNumber = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Số điện thoại'
    )
    Email = models.EmailField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Email'
    )
    RegisterDate = models.DateTimeField(
        default=timezone.now,
        verbose_name='Ngày đăng ký'
    )
    LoyaltyPoints = models.IntegerField(
        default=0,
        verbose_name='Điểm thành viên'
    )
    
    class Meta:
        db_table = 'KhachHang'
        verbose_name = 'Khách hàng'
        verbose_name_plural = 'Khách hàng'
        ordering = ['-RegisterDate']
        indexes = [
            models.Index(fields=['PhoneNumber']),
            models.Index(fields=['Email']),
        ]
    
    def __str__(self):
        return f"{self.FullName} - {self.PhoneNumber}"
    
    @property
    def membership_level(self):
        """Xác định cấp độ thành viên dựa trên điểm"""
        if self.LoyaltyPoints >= 1000:
            return 'VIP'
        elif self.LoyaltyPoints >= 500:
            return 'Gold'
        elif self.LoyaltyPoints >= 100:
            return 'Silver'
        return 'Bronze'
