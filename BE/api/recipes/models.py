"""
Models Layer - Công thức
"""
from django.db import models
from api.products.models import SanPham
from api.ingredients.models import NguyenLieu


class CongThuc(models.Model):
    """Model cho công thức (Recipe) - Nguyên liệu cho mỗi sản phẩm"""
    ProductID = models.ForeignKey(
        SanPham,
        on_delete=models.CASCADE,
        verbose_name='Sản phẩm'
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
    Unit = models.CharField(max_length=20, verbose_name='Đơn vị')
    
    class Meta:
        db_table = 'CongThuc'
        verbose_name = 'Công thức'
        verbose_name_plural = 'Công thức'
        unique_together = [['ProductID', 'IngredientID']]
        indexes = [
            models.Index(fields=['ProductID']),
            models.Index(fields=['IngredientID']),
        ]
    
    def __str__(self):
        return f"{self.ProductID.ProductName} - {self.IngredientID.IngredientName}"
