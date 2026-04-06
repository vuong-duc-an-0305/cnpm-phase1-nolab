"""
Admin configuration cho Orders
"""
from django.contrib import admin
from .models import HoaDon, ChiTietDonHang


class ChiTietDonHangInline(admin.TabularInline):
    model = ChiTietDonHang
    extra = 0
    readonly_fields = ['Subtotal']


@admin.register(HoaDon)
class HoaDonAdmin(admin.ModelAdmin):
    list_display = [
        'OrderID', 'CustomerID', 'EmployeeID', 'OrderDate',
        'TotalAmount', 'Discount', 'FinalAmount', 'PaymentMethod', 'Status'
    ]
    list_filter = ['Status', 'PaymentMethod', 'OrderDate']
    search_fields = [
        'OrderID', 'CustomerID__FullName',
        'CustomerID__PhoneNumber', 'EmployeeID__FullName'
    ]
    ordering = ['-OrderDate']
    list_per_page = 20
    readonly_fields = ['OrderDate', 'TotalAmount', 'FinalAmount']
    inlines = [ChiTietDonHangInline]
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('CustomerID', 'EmployeeID', 'OrderDate')
        }),
        ('Thanh toán', {
            'fields': ('TotalAmount', 'Discount', 'FinalAmount', 'PaymentMethod')
        }),
        ('Trạng thái', {
            'fields': ('Status',)
        }),
    )


@admin.register(ChiTietDonHang)
class ChiTietDonHangAdmin(admin.ModelAdmin):
    list_display = [
        'OrderDetailID', 'OrderID', 'ProductID',
        'Quantity', 'UnitPrice', 'Subtotal', 'ToppingNote'
    ]
    list_filter = ['OrderID__OrderDate', 'ProductID']
    search_fields = ['OrderID__OrderID', 'ProductID__ProductName']
    ordering = ['-OrderID__OrderDate']
    list_per_page = 20
    readonly_fields = ['Subtotal']
