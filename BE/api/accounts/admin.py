"""
Admin configuration for Employee Details
"""
from django.contrib import admin
from .models import EmployeeDetail


@admin.register(EmployeeDetail)
class EmployeeDetailAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'full_name',
        'phone_number',
        'hire_date',
    ]
    list_filter = ['gender', 'hire_date']
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'phone_number',
        'citizen_id',
    ]
    readonly_fields = ['user', 'hire_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin người dùng', {
            'fields': ('user', 'avatar')
        }),
        ('Thông tin cá nhân', {
            'fields': (
                'phone_number',
                'citizen_id',
                'gender',
                'date_of_birth',
                'address',
            )
        }),
        ('Liên hệ khẩn cấp', {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_phone',
                'emergency_contact_relationship',
            )
        }),
        ('Thông tin công việc', {
            'fields': (
                'hire_date',
                'salary',
            )
        }),
        ('Ghi chú', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
