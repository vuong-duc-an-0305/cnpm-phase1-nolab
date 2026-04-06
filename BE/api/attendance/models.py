"""
Models for attendance and work schedule management
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class WorkSchedule(models.Model):
    """
    Lịch làm việc của nhân viên - Có thể thay đổi linh hoạt theo thời gian
    """
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='work_schedules',
        verbose_name='Nhân viên'
    )
    schedule_date = models.DateField(
        verbose_name='Ngày làm việc'
    )
    shift_start_time = models.TimeField(
        verbose_name='Giờ bắt đầu ca'
    )
    shift_end_time = models.TimeField(
        verbose_name='Giờ kết thúc ca'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ghi chú'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    class Meta:
        db_table = 'work_schedules'
        verbose_name = 'Lịch làm việc'
        verbose_name_plural = 'Lịch làm việc'
        ordering = ['-schedule_date', 'shift_start_time']
        indexes = [
            models.Index(fields=['employee', 'schedule_date']),
            models.Index(fields=['schedule_date']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['employee', 'schedule_date', 'shift_start_time']

    def clean(self):
        """Validate schedule data"""
        from django.utils import timezone
        
        errors = {}
        
        # Validate giờ kết thúc phải sau giờ bắt đầu
        if self.shift_end_time <= self.shift_start_time:
            errors['shift_end_time'] = 'Giờ kết thúc phải sau giờ bắt đầu'
        
        # Validate không cho tạo lịch với thời điểm đã qua
        now = timezone.localtime(timezone.now())
        current_date = now.date()
        current_time = now.time()
        
        # Chỉ validate khi tạo mới (không có pk)
        if not self.pk:
            # Nếu ngày làm việc là ngày hôm nay
            if self.schedule_date == current_date:
                # Kiểm tra giờ bắt đầu phải sau thời điểm hiện tại
                if self.shift_start_time < current_time:
                    errors['shift_start_time'] = f'Giờ bắt đầu ({self.shift_start_time}) không thể trước thời điểm hiện tại ({current_time.strftime("%H:%M")})'
                # Kiểm tra giờ kết thúc phải sau thời điểm hiện tại
                if self.shift_end_time < current_time:
                    errors['shift_end_time'] = f'Giờ kết thúc ({self.shift_end_time}) không thể trước thời điểm hiện tại ({current_time.strftime("%H:%M")})'
            # Nếu ngày làm việc là ngày trong quá khứ
            elif self.schedule_date < current_date:
                errors['schedule_date'] = f'Không thể tạo lịch cho ngày trong quá khứ ({self.schedule_date})'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.username} - {self.schedule_date} ({self.shift_start_time} - {self.shift_end_time})"

    @property
    def scheduled_hours(self):
        """Tính số giờ dự kiến làm việc"""
        from datetime import datetime, timedelta
        
        start = datetime.combine(datetime.today(), self.shift_start_time)
        end = datetime.combine(datetime.today(), self.shift_end_time)
        
        # Nếu ca qua đêm
        if end <= start:
            end += timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600


class AttendanceRecord(models.Model):
    """
    Bản ghi chấm công nhân viên
    1 tiếng = 1 công, tối đa 16 công/ngày
    """
    
    STATUS_CHOICES = [
        ('PRESENT', 'Có mặt'),
        ('ABSENT', 'Vắng mặt'),
        ('LATE', 'Đi muộn'),
        ('EARLY_LEAVE', 'Về sớm'),
        ('OVERTIME', 'Tăng ca'),
        ('LEAVE', 'Nghỉ phép'),
        ('SICK_LEAVE', 'Nghỉ ốm'),
    ]

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name='Nhân viên'
    )
    date = models.DateField(
        verbose_name='Ngày',
        db_index=True  # Index cho queries theo ngày
    )
    check_in_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Giờ vào'
    )
    check_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Giờ ra'
    )
    work_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('16.00'))  # Tối đa 16 công/ngày
        ],
        verbose_name='Số công (giờ)',
        help_text='1 giờ = 1 công, tối đa 16 công/ngày'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PRESENT',
        verbose_name='Trạng thái',
        db_index=True  # Index cho filter theo trạng thái
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ghi chú'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendances',
        verbose_name='Người duyệt'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Thời gian duyệt'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    class Meta:
        db_table = 'attendance_records'
        verbose_name = 'Bản ghi chấm công'
        verbose_name_plural = 'Bản ghi chấm công'
        ordering = ['-date', '-check_in_time']
        indexes = [
            # Compound indexes cho queries phức tạp
            models.Index(fields=['employee', 'date'], name='idx_emp_date'),
            models.Index(fields=['date', 'status'], name='idx_date_status'),
            models.Index(fields=['employee', 'date', 'status'], name='idx_emp_date_status'),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['employee', '-date']),
        ]
        unique_together = ['employee', 'date']

    def clean(self):
        """Validate attendance data"""
        errors = {}
        
        # Validate work_hours không vượt quá 16
        if self.work_hours and self.work_hours > Decimal('16.00'):
            errors['work_hours'] = 'Số công không được vượt quá 16 công/ngày'
        
        # Validate check_in và check_out
        if self.check_in_time and self.check_out_time:
            if self.check_out_time <= self.check_in_time:
                errors['check_out_time'] = 'Giờ ra phải sau giờ vào'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Tự động tính work_hours nếu có check_in và check_out
        if self.check_in_time and self.check_out_time and not self.work_hours:
            self.work_hours = self.calculate_work_hours()
        
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.username} - {self.date} ({self.work_hours} công)"

    def calculate_work_hours(self):
        """
        Tính số giờ làm việc dựa trên lịch làm việc (WorkSchedule)
        - Nếu có lịch: Tính dựa trên giờ thực tế so với lịch
        - Nếu không có lịch: Tính từ check_in và check_out
        - Tự động đánh dấu OVERTIME nếu vượt lịch > 1 giờ
        - Tự động đánh dấu LATE nếu vào muộn > 15 phút
        - Trả về giá trị tối đa 16 công
        """
        if not self.check_in_time or not self.check_out_time:
            return Decimal('0.00')
        
        from datetime import datetime, timedelta
        
        # Lấy lịch làm việc trong ngày
        try:
            schedule = WorkSchedule.objects.filter(
                employee=self.employee,
                schedule_date=self.date,
                is_active=True
            ).first()
        except:
            schedule = None
        
        start = datetime.combine(datetime.today(), self.check_in_time)
        end = datetime.combine(datetime.today(), self.check_out_time)
        
        # Nếu check_out qua ngày hôm sau
        if end <= start:
            end += timedelta(days=1)
        
        duration = end - start
        actual_hours = Decimal(str(duration.total_seconds() / 3600))
        
        # Làm tròn đến 2 chữ số thập phân
        actual_hours = actual_hours.quantize(Decimal('0.01'))
        
        # Nếu có lịch làm việc, so sánh và cập nhật status
        if schedule:
            schedule_start = datetime.combine(datetime.today(), schedule.shift_start_time)
            schedule_end = datetime.combine(datetime.today(), schedule.shift_end_time)
            
            if schedule_end <= schedule_start:
                schedule_end += timedelta(days=1)
            
            scheduled_duration = schedule_end - schedule_start
            scheduled_hours = Decimal(str(scheduled_duration.total_seconds() / 3600))
            
            # Check đi muộn (> 15 phút)
            late_minutes = (start - schedule_start).total_seconds() / 60
            if late_minutes > 15 and self.status == 'PRESENT':
                self.status = 'LATE'
            
            # Check làm thêm giờ (vượt lịch > 1 giờ)
            overtime_hours = actual_hours - scheduled_hours
            if overtime_hours > Decimal('1.00') and self.status in ['PRESENT', 'LATE']:
                self.status = 'OVERTIME'
            
            # Tính công dựa trên lịch
            # Nếu làm đủ hoặc hơn lịch: tính theo thực tế
            # Nếu làm thiếu: tính theo thực tế (sẽ bị trừ lương)
            work_hours = actual_hours
        else:
            # Không có lịch: tính trực tiếp từ check_in/check_out
            work_hours = actual_hours
        
        # Giới hạn tối đa 16 công
        return min(work_hours, Decimal('16.00'))
