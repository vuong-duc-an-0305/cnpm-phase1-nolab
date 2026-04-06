"""
Admin configuration cho Ingredients
"""
from django.contrib import admin
from .models import NguyenLieu


@admin.register(NguyenLieu)
class NguyenLieuAdmin(admin.ModelAdmin):
    list_display = ['IngredientID', 'IngredientName', 'Unit', 'QuantityInStock', 'MinQuantity', 'is_low_stock']
    search_fields = ['IngredientName']
    ordering = ['IngredientName']
    list_per_page = 20
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Sắp hết'
