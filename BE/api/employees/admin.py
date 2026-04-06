"""
Admin configuration cho Employees
"""
from django.contrib import admin
from .models import NhanVien


@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    list_display = ['EmployeeID', 'FullName', 'PhoneNumber', 'JobTitle', 'WorkShift']
    list_filter = ['WorkShift', 'JobTitle']
    search_fields = ['FullName', 'PhoneNumber', 'JobTitle']
    ordering = ['FullName']
    list_per_page = 20
