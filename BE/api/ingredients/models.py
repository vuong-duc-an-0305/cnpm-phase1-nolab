"""
Models Layer - Nguyên liệu
"""
from django.db import models


class NguyenLieu(models.Model):
    """Model cho nguyên liệu (Ingredient)"""
    IngredientID = models.AutoField(primary_key=True)
    IngredientName = models.CharField(max_length=200, verbose_name='Tên nguyên liệu')
    Unit = models.CharField(max_length=20, default='', blank=True, verbose_name='Đơn vị')
    QuantityInStock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
        verbose_name='Số lượng tồn kho'
    )
    MinQuantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
        verbose_name='Số lượng tối thiểu'
    )
    
    class Meta:
        db_table = 'NguyenLieu'
        verbose_name = 'Nguyên liệu'
        verbose_name_plural = 'Nguyên liệu'
        ordering = ['IngredientName']
    
    def __str__(self):
        return self.IngredientName
    
    @property
    def is_low_stock(self):
        """Kiểm tra nguyên liệu sắp hết"""
        return self.QuantityInStock <= self.MinQuantity
    
    @property
    def stock_percentage(self):
        """Tính phần trăm tồn kho so với mức tối thiểu"""
        if self.MinQuantity == 0:
            return 100
        return (self.QuantityInStock / self.MinQuantity) * 100
