"""
Models Layer - Danh mục sản phẩm
"""
from django.db import models


class DanhMucSanPham(models.Model):
    """Model cho danh mục sản phẩm (Category)"""
    CategoryID = models.AutoField(primary_key=True)
    CategoryName = models.CharField(max_length=100, verbose_name='Tên danh mục')
    
    class Meta:
        db_table = 'DanhMucSanPham'
        verbose_name = 'Danh mục sản phẩm'
        verbose_name_plural = 'Danh mục sản phẩm'
        ordering = ['CategoryName']
    
    def __str__(self):
        return self.CategoryName
