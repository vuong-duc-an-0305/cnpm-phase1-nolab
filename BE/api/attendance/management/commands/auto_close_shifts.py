"""
Management command to automatically close shifts that have ended without check-in
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from api.attendance.models import WorkSchedule, AttendanceRecord
from decimal import Decimal


class Command(BaseCommand):
    help = 'Tự động kết thúc các ca làm việc đã hết giờ mà chưa check-in với trạng thái nghỉ làm'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Chỉ hiển thị các ca sẽ bị đóng mà không thực hiện thay đổi',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        current_date = now.date()

        self.stdout.write(self.style.SUCCESS(
            f'\n=== Kiểm tra các ca làm việc đã kết thúc ({current_date} {current_time}) ==='
        ))

        # Lấy tất cả các lịch làm việc active trong ngày hôm nay đã kết thúc
        schedules_to_close = WorkSchedule.objects.filter(
            schedule_date=current_date,
            is_active=True,
            shift_end_time__lt=current_time
        ).select_related('employee')

        closed_count = 0
        skipped_count = 0

        for schedule in schedules_to_close:
            # Kiểm tra xem đã có attendance record chưa
            attendance_exists = AttendanceRecord.objects.filter(
                employee=schedule.employee,
                date=schedule.schedule_date
            ).exists()

            if not attendance_exists:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Sẽ đóng ca: {schedule.employee.username} - '
                        f'{schedule.schedule_date} ({schedule.shift_start_time} - {schedule.shift_end_time})'
                    )
                else:
                    # Tạo attendance record với trạng thái ABSENT
                    AttendanceRecord.objects.create(
                        employee=schedule.employee,
                        date=schedule.schedule_date,
                        check_in_time=None,
                        check_out_time=None,
                        work_hours=Decimal('0.00'),
                        status='ABSENT',
                        notes=f'Tự động đóng ca - Không check-in trong ca làm việc ({schedule.shift_start_time} - {schedule.shift_end_time})'
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f'Đã đóng ca: {schedule.employee.username} - '
                            f'{schedule.schedule_date} ({schedule.shift_start_time} - {schedule.shift_end_time}) - '
                            f'Trạng thái: ABSENT'
                        )
                    )
                closed_count += 1
            else:
                skipped_count += 1

        # Tổng kết
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Tổng kết ==='
        ))
        if dry_run:
            self.stdout.write(f'Số ca sẽ bị đóng: {closed_count}')
        else:
            self.stdout.write(f'Số ca đã đóng: {closed_count}')
        self.stdout.write(f'Số ca đã có attendance (bỏ qua): {skipped_count}')
        
        if dry_run:
            self.stdout.write(
                self.style.NOTICE('\nĐây là chế độ dry-run. Chạy lại không có --dry-run để thực hiện thay đổi.')
            )
