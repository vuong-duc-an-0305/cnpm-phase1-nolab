"""
Admin configuration for Attendance Management
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AttendanceRecord, WorkSchedule


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'schedule_date',
        'shift_start_time',
        'shift_end_time',
        'scheduled_hours',
        'is_active',
    ]
    list_filter = ['is_active', 'schedule_date', 'employee']
    search_fields = [
        'employee__username',
        'employee__first_name',
        'employee__last_name',
    ]
    date_hierarchy = 'schedule_date'
    readonly_fields = ['created_at', 'updated_at', 'scheduled_hours']
    
    fieldsets = (
        ('Thông tin nhân viên', {
            'fields': ('employee',)
        }),
        ('Thông tin ca làm', {
            'fields': (
                'schedule_date',
                'shift_start_time',
                'shift_end_time',
                'scheduled_hours',
                'is_active',
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

    def scheduled_hours(self, obj):
        """Display scheduled hours"""
        return f"{obj.scheduled_hours:.2f} giờ"
    scheduled_hours.short_description = 'Số giờ dự kiến'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'date',
        'check_in_time',
        'check_out_time',
        'work_hours_display',
        'status_badge',
        'approved_status',
    ]
    list_filter = ['status', 'date', 'employee']
    search_fields = [
        'employee__username',
        'employee__first_name',
        'employee__last_name',
        'notes',
    ]
    date_hierarchy = 'date'
    readonly_fields = [
        'created_at',
        'updated_at',
        'approved_at',
        'work_hours_calculated',
    ]
    
    fieldsets = (
        ('Thông tin nhân viên', {
            'fields': ('employee', 'date')
        }),
        ('Thời gian làm việc', {
            'fields': (
                'check_in_time',
                'check_out_time',
                'work_hours',
                'work_hours_calculated',
            )
        }),
        ('Trạng thái', {
            'fields': ('status', 'notes')
        }),
        ('Phê duyệt', {
            'fields': (
                'approved_by',
                'approved_at',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def work_hours_display(self, obj):
        """Display work hours with max limit indicator"""
        hours = obj.work_hours
        if hours >= 16:
            return format_html(
                '<span style="color: red; font-weight: bold;">{} công (MAX)</span>',
                hours
            )
        elif hours >= 12:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} công</span>',
                hours
            )
        return f"{hours} công"
    work_hours_display.short_description = 'Số công'

    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'PRESENT': 'green',
            'ABSENT': 'red',
            'LATE': 'orange',
            'EARLY_LEAVE': 'orange',
            'OVERTIME': 'blue',
            'LEAVE': 'gray',
            'SICK_LEAVE': 'purple',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Trạng thái'

    def approved_status(self, obj):
        """Display approval status"""
        if obj.approved_by and obj.approved_at:
            return format_html(
                '<span style="color: green;">✓ Đã duyệt bởi {}</span>',
                obj.approved_by.username
            )
        return format_html('<span style="color: gray;">Chưa duyệt</span>')
    approved_status.short_description = 'Phê duyệt'

    def work_hours_calculated(self, obj):
        """Show calculated work hours from check in/out times"""
        if obj.check_in_time and obj.check_out_time:
            calculated = obj.calculate_work_hours()
            return f"{calculated} giờ (tự động tính)"
        return "N/A"
    work_hours_calculated.short_description = 'Số giờ tính toán'
