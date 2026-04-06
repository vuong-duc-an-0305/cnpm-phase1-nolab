"""
Models Layer - Phiếu nhập kho và Chi tiết nhập kho
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from api.ingredients.models import NguyenLieu


class PhieuNhapKho(models.Model):
    """Model cho phiếu nhập kho (Import Receipt)"""
    ImportID = models.AutoField(primary_key=True)
    EmployeeID = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Nhân viên',
        related_name='imports'
    )
    ImportDate = models.DateTimeField(
        default=timezone.now,
        verbose_name='Ngày nhập'
    )
    TotalAmount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Tổng tiền'
    )
    
    class Meta:
        db_table = 'PhieuNhapKho'
        verbose_name = 'Phiếu nhập kho'
        verbose_name_plural = 'Phiếu nhập kho'
        ordering = ['-ImportDate']
        indexes = [
            models.Index(fields=['ImportDate']),
            models.Index(fields=['EmployeeID']),
        ]
    
    def __str__(self):
        return f"NK{self.ImportID} - {self.ImportDate.strftime('%d/%m/%Y')}"
    
    def calculate_total(self):
        """Tính tổng tiền từ chi tiết nhập kho"""
        total = sum(
            detail.Quantity * detail.UnitPrice
            for detail in self.chitietnhapkho_set.all()
        )
        return total


class ChiTietNhapKho(models.Model):
    """Model cho chi tiết nhập kho (Import Detail)"""
    ImportID = models.ForeignKey(
        PhieuNhapKho,
        on_delete=models.CASCADE,
        verbose_name='Phiếu nhập kho'
    )
    IngredientID = models.ForeignKey(
        NguyenLieu,
        on_delete=models.PROTECT,
        verbose_name='Nguyên liệu'
    )
    Quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name='Số lượng'
    )
    UnitPrice = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Đơn giá'
    )
    
    class Meta:
        db_table = 'ChiTietNhapKho'
        verbose_name = 'Chi tiết nhập kho'
        verbose_name_plural = 'Chi tiết nhập kho'
        unique_together = [['ImportID', 'IngredientID']]
        indexes = [
            models.Index(fields=['ImportID']),
            models.Index(fields=['IngredientID']),
        ]
    
    def __str__(self):
        return f"{self.ImportID} - {self.IngredientID.IngredientName}"
    
    @property
    def subtotal(self):
        """Tính thành tiền"""
        return self.Quantity * self.UnitPrice
