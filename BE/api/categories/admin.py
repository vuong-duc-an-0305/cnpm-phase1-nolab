"""
Admin configuration cho Categories
"""
from django.contrib import admin
from .models import DanhMucSanPham


@admin.register(DanhMucSanPham)
class DanhMucSanPhamAdmin(admin.ModelAdmin):
    list_display = ['CategoryID', 'CategoryName']
    search_fields = ['CategoryName']
    ordering = ['CategoryName']
