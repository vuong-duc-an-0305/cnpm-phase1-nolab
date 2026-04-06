"""
Serializers for Attendance Management
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AttendanceRecord, WorkSchedule
from decimal import Decimal


class WorkScheduleSerializer(serializers.ModelSerializer):
    """Serializer for WorkSchedule model"""
    
    employee_name = serializers.CharField(
        source='employee.get_full_name',
        read_only=True
    )
    employee_username = serializers.CharField(
        source='employee.username',
        read_only=True
    )
    scheduled_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = WorkSchedule
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_username',
            'schedule_date',
            'shift_start_time',
            'shift_end_time',
            'scheduled_hours',
            'is_active',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Validate schedule data"""
        from django.utils import timezone
        
        shift_start = data.get('shift_start_time')
        shift_end = data.get('shift_end_time')
        schedule_date = data.get('schedule_date')
        
        errors = {}
        
        # Validate giờ kết thúc phải sau giờ bắt đầu
        if shift_start and shift_end and shift_end <= shift_start:
            errors['shift_end_time'] = 'Giờ kết thúc phải sau giờ bắt đầu'
        
        # Validate không cho tạo lịch với thời điểm đã qua (chỉ khi tạo mới)
        if not self.instance and schedule_date:
            now = timezone.localtime(timezone.now())
            current_date = now.date()
            current_time = now.time()
            
            # Nếu ngày làm việc là ngày trong quá khứ
            if schedule_date < current_date:
                errors['schedule_date'] = f'Không thể tạo lịch cho ngày trong quá khứ ({schedule_date})'
            # Nếu ngày làm việc là ngày hôm nay
            elif schedule_date == current_date:
                if shift_start and shift_start < current_time:
                    errors['shift_start_time'] = f'Giờ bắt đầu không thể trước thời điểm hiện tại ({current_time.strftime("%H:%M")})'
                if shift_end and shift_end < current_time:
                    errors['shift_end_time'] = f'Giờ kết thúc không thể trước thời điểm hiện tại ({current_time.strftime("%H:%M")})'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceRecord model"""
    
    employee_name = serializers.CharField(
        source='employee.get_full_name',
        read_only=True
    )
    employee_username = serializers.CharField(
        source='employee.username',
        read_only=True
    )
    approved_by_username = serializers.CharField(
        source='approved_by.username',
        read_only=True,
        allow_null=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = AttendanceRecord
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_username',
            'date',
            'check_in_time',
            'check_out_time',
            'work_hours',
            'status',
            'status_display',
            'notes',
            'approved_by',
            'approved_by_username',
            'approved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['approved_at', 'created_at', 'updated_at']

    def validate_work_hours(self, value):
        """Validate work hours is within limit"""
        if value > Decimal('16.00'):
            raise serializers.ValidationError(
                'Số công không được vượt quá 16 công/ngày'
            )
        if value < Decimal('0.00'):
            raise serializers.ValidationError(
                'Số công phải lớn hơn hoặc bằng 0'
            )
        return value

    def validate(self, data):
        """Validate attendance data"""
        check_in = data.get('check_in_time')
        check_out = data.get('check_out_time')
        
        # If both check_in and check_out are provided, validate order
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({
                'check_out_time': 'Giờ ra phải sau giờ vào'
            })
        
        return data

    def create(self, validated_data):
        """Create attendance record with auto-calculated work_hours"""
        instance = AttendanceRecord(**validated_data)
        
        # Auto calculate work_hours if not provided but check times are
        if (not validated_data.get('work_hours') and 
            validated_data.get('check_in_time') and 
            validated_data.get('check_out_time')):
            instance.work_hours = instance.calculate_work_hours()
        
        instance.save()
        return instance


class AttendanceSummarySerializer(serializers.Serializer):
    """Serializer for attendance summary statistics"""
    
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    employee_username = serializers.CharField()
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    total_work_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_days_present = serializers.IntegerField()
    total_days_absent = serializers.IntegerField()
    total_days_late = serializers.IntegerField()
    total_overtime_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    average_work_hours_per_day = serializers.DecimalField(max_digits=5, decimal_places=2)


class SalaryCalculationSerializer(serializers.Serializer):
    """Serializer for salary calculation"""
    
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    employee_username = serializers.CharField()
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    base_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    actual_work_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    max_work_hours_in_month = serializers.DecimalField(max_digits=8, decimal_places=2)
    work_hours_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    calculated_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    bonus = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    details = serializers.DictField(child=serializers.CharField(), required=False)
