"""
Admin configuration cho Products
"""
from django.contrib import admin
from .models import SanPham
from api.recipes.models import CongThuc


class CongThucInline(admin.TabularInline):
    model = CongThuc
    extra = 1
    autocomplete_fields = ['IngredientID']
    fields = ['IngredientID', 'Quantity', 'Unit']


@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ['ProductID', 'ProductName', 'Price', 'CategoryID', 'Status']
    list_filter = ['Status', 'CategoryID']
    search_fields = ['ProductName', 'CategoryID__CategoryName']
    ordering = ['ProductName']
    list_per_page = 20
    inlines = [CongThucInline]
