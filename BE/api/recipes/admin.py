"""
Admin configuration cho Recipes
"""
from django.contrib import admin
from .models import CongThuc


@admin.register(CongThuc)
class CongThucAdmin(admin.ModelAdmin):
    list_display = ['ProductID', 'IngredientID', 'Quantity', 'Unit']
    list_filter = ['ProductID', 'IngredientID']
    search_fields = ['ProductID__ProductName', 'IngredientID__IngredientName']
    ordering = ['ProductID', 'IngredientID']
    list_per_page = 20
