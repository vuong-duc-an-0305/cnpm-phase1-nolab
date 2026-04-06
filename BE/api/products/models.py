"""
Models Layer - Sản phẩm
"""
from django.db import models
from api.categories.models import DanhMucSanPham


class SanPham(models.Model):
    """Model cho sản phẩm (Product)"""
    
    STATUS_CHOICES = [
        (0, 'Hết hàng'),
        (1, 'Còn hàng'),
        (2, 'Ngừng kinh doanh'),
    ]
    
    ProductID = models.AutoField(primary_key=True)
    ProductName = models.CharField(max_length=200, verbose_name='Tên sản phẩm')
    Price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá')
    ImageUrl = models.CharField(max_length=255, blank=True, null=True, verbose_name='Hình ảnh')
    CategoryID = models.ForeignKey(
        DanhMucSanPham,
        on_delete=models.PROTECT,
        verbose_name='Danh mục'
    )
    Status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        verbose_name='Trạng thái'
    )
    
    class Meta:
        db_table = 'SanPham'
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['ProductName']
        indexes = [
            models.Index(fields=['CategoryID']),
            models.Index(fields=['Status']),
        ]
    
    def __str__(self):
        return self.ProductName
    
    @property
    def is_available(self):
        """Kiểm tra sản phẩm có sẵn không"""
        return self.Status == 1
