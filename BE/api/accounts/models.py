"""
Models for Employee Details - Thông tin chi tiết nhân viên
"""
from django.db import models
from django.contrib.auth.models import User


class EmployeeDetail(models.Model):
    """Model lưu thông tin chi tiết của nhân viên"""
    
    GENDER_CHOICES = [
        ('MALE', 'Nam'),
        ('FEMALE', 'Nữ'),
        ('OTHER', 'Khác'),
    ]
    
    # Link với User qua username (unique)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='employee_detail',
        verbose_name='Người dùng'
    )
    
    # Thông tin cá nhân
    avatar = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ảnh đại diện'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Số điện thoại'
    )
    
    citizen_id = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        verbose_name='CCCD/CMND'
    )
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='OTHER',
        verbose_name='Giới tính'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày sinh'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Địa chỉ'
    )
    
    # Thông tin liên hệ khẩn cấp
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Người liên hệ khẩn cấp'
    )
    
    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='SĐT người liên hệ khẩn cấp'
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Mối quan hệ'
    )
    
    # Thông tin công việc
    hire_date = models.DateField(
        auto_now_add=True,
        verbose_name='Ngày vào làm'
    )
    
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Lương cơ bản'
    )
    
    # Ghi chú
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ghi chú'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    class Meta:
        db_table = 'employee_details'
        verbose_name = 'Chi tiết nhân viên'
        verbose_name_plural = 'Chi tiết nhân viên'
        indexes = [
            models.Index(fields=['hire_date']),
            models.Index(fields=['salary']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"Detail for {self.user.username}"
    
    @property
    def full_name(self):
        """Lấy họ tên đầy đủ từ User"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
