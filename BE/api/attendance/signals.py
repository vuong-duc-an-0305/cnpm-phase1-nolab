"""
Signals for Attendance app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkSchedule, AttendanceRecord


@receiver(post_save, sender=WorkSchedule)
def create_attendance_record_on_schedule(sender, instance, created, **kwargs):
    """
    Tự động tạo bản ghi chấm công khi tạo lịch làm việc mới
    """
    if created and instance.is_active:
        # Kiểm tra xem đã có attendance record cho ngày này chưa
        existing = AttendanceRecord.objects.filter(
            employee=instance.employee,
            date=instance.schedule_date
        ).exists()
        
        if not existing:
            # Tạo attendance record mới với status mặc định
            AttendanceRecord.objects.create(
                employee=instance.employee,
                date=instance.schedule_date,
                status='PRESENT',
                notes=f'Tự động tạo từ lịch làm việc: {instance.shift_start_time} - {instance.shift_end_time}'
            )
