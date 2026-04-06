"""
Admin configuration cho Customers
"""
from django.contrib import admin
from .models import KhachHang


@admin.register(KhachHang)
class KhachHangAdmin(admin.ModelAdmin):
    list_display = ['CustomerID', 'FullName', 'PhoneNumber', 'Email', 'LoyaltyPoints', 'membership_level', 'RegisterDate']
    list_filter = ['RegisterDate']
    search_fields = ['FullName', 'PhoneNumber', 'Email']
    ordering = ['-RegisterDate']
    list_per_page = 20
    readonly_fields = ['RegisterDate']
    
    def membership_level(self, obj):
        return obj.membership_level
    membership_level.short_description = 'Cấp độ'
