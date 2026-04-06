"""
Admin configuration cho Inventory
"""
from django.contrib import admin
from .models import PhieuNhapKho, ChiTietNhapKho


class ChiTietNhapKhoInline(admin.TabularInline):
    model = ChiTietNhapKho
    extra = 0


@admin.register(PhieuNhapKho)
class PhieuNhapKhoAdmin(admin.ModelAdmin):
    list_display = ['ImportID', 'EmployeeID', 'ImportDate', 'TotalAmount']
    list_filter = ['ImportDate']
    search_fields = ['ImportID', 'EmployeeID__FullName']
    ordering = ['-ImportDate']
    list_per_page = 20
    readonly_fields = ['ImportDate', 'TotalAmount']
    inlines = [ChiTietNhapKhoInline]


@admin.register(ChiTietNhapKho)
class ChiTietNhapKhoAdmin(admin.ModelAdmin):
    list_display = ['ImportID', 'IngredientID', 'Quantity', 'UnitPrice', 'subtotal']
    list_filter = ['ImportID__ImportDate', 'IngredientID']
    search_fields = ['ImportID__ImportID', 'IngredientID__IngredientName']
    ordering = ['-ImportID__ImportDate']
    list_per_page = 20
    
    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Thành tiền'
