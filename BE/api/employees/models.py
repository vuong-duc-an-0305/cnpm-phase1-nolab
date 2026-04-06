"""
Models Layer - Nhân viên
"""
from django.db import models


class NhanVien(models.Model):
    """Model cho nhân viên (Employee)"""
    
    SHIFT_CHOICES = [
        ('SANG', 'Ca sáng'),
        ('CHIEU', 'Ca chiều'),
        ('TOI', 'Ca tối'),
        ('FULL', 'Full time'),
    ]
    
    EmployeeID = models.AutoField(primary_key=True)
    FullName = models.CharField(max_length=150, verbose_name='Họ tên')
    PhoneNumber = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Số điện thoại'
    )
    JobTitle = models.CharField(
        max_length=100,
        verbose_name='Chức vụ',
        help_text='VD: Pha chế, Thu ngân, Quản lý'
    )
    WorkShift = models.CharField(
        max_length=50,
        choices=SHIFT_CHOICES,
        default='FULL',
        verbose_name='Ca làm việc'
    )
    
    class Meta:
        db_table = 'NhanVien'
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'
        ordering = ['FullName']
        indexes = [
            models.Index(fields=['PhoneNumber']),
            models.Index(fields=['WorkShift']),
        ]
    
    def __str__(self):
        return f"{self.FullName} - {self.JobTitle}"
