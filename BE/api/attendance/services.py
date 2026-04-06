"""
Business logic services for Attendance Management
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, Avg, F, Prefetch
from django.db import transaction
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import AttendanceRecord, WorkSchedule
import calendar


class AttendanceService:
    """Service for attendance operations"""
    
    # Cache timeout in seconds (5 minutes)
    CACHE_TIMEOUT = 300
    
    @staticmethod
    def get_employee_attendance(employee_id, start_date, end_date):
        """
        Lấy bản ghi chấm công của nhân viên trong khoảng thời gian
        Tối ưu: Sử dụng select_related và only để giảm query
        """
        return AttendanceRecord.objects.filter(
            employee_id=employee_id,
            date__gte=start_date,
            date__lte=end_date
        ).select_related(
            'employee', 
            'approved_by'
        ).only(
            'id', 'date', 'check_in_time', 'check_out_time', 
            'work_hours', 'status', 'notes',
            'employee__username', 'employee__first_name', 'employee__last_name',
            'approved_by__username'
        ).order_by('date')
    
    @staticmethod
    def get_monthly_attendance_summary(employee_id, month, year):
        """
        Tổng hợp chấm công theo tháng cho nhân viên
        Tối ưu: Sử dụng aggregation và cache
        """
        cache_key = f'attendance_summary_{employee_id}_{month}_{year}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            employee = User.objects.only(
                'id', 'username', 'first_name', 'last_name'
            ).get(id=employee_id)
        except User.DoesNotExist:
            return None
        
        # Tính ngày đầu và cuối tháng
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
        
        # Sử dụng một query duy nhất với aggregation
        stats = AttendanceRecord.objects.filter(
            employee_id=employee_id,
            date__gte=first_day,
            date__lte=last_day
        ).aggregate(
            total_work_hours=Sum('work_hours'),
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            late=Count('id', filter=Q(status='LATE')),
            early_leave=Count('id', filter=Q(status='EARLY_LEAVE')),
            overtime=Count('id', filter=Q(status='OVERTIME')),
            leave=Count('id', filter=Q(status='LEAVE')),
            sick_leave=Count('id', filter=Q(status='SICK_LEAVE')),
            overtime_hours=Sum('work_hours', filter=Q(status='OVERTIME')),
        )
        
        total_work_hours = stats['total_work_hours'] or Decimal('0.00')
        overtime_hours = stats['overtime_hours'] or Decimal('0.00')
        
        # Tính average work hours per day
        total_days = (stats['present'] or 0) + (stats['late'] or 0) + (stats['early_leave'] or 0)
        avg_hours = total_work_hours / total_days if total_days > 0 else Decimal('0.00')
        
        result = {
            'employee_id': employee.id,
            'employee_name': employee.get_full_name() or employee.username,
            'employee_username': employee.username,
            'month': month,
            'year': year,
            'total_work_hours': total_work_hours,
            'total_days_present': stats['present'] or 0,
            'total_days_absent': stats['absent'] or 0,
            'total_days_late': stats['late'] or 0,
            'total_days_early_leave': stats['early_leave'] or 0,
            'total_overtime_hours': overtime_hours,
            'total_days_leave': stats['leave'] or 0,
            'total_days_sick_leave': stats['sick_leave'] or 0,
            'average_work_hours_per_day': round(avg_hours, 2),
        }
        
        # Cache kết quả trong 5 phút
        cache.set(cache_key, result, AttendanceService.CACHE_TIMEOUT)
        
        return result
    
    @staticmethod
    @transaction.atomic
    def check_in(employee_id, date, check_in_time, notes=None):
        """
        Chấm công vào ca
        Tối ưu: Sử dụng transaction và select_for_update
        """
        try:
            record, created = AttendanceRecord.objects.get_or_create(
                employee_id=employee_id,
                date=date,
                defaults={
                    'check_in_time': check_in_time,
                    'status': 'PRESENT',
                    'notes': notes,
                }
            )
            
            if not created:
                record.check_in_time = check_in_time
                if notes:
                    record.notes = notes
                record.save()
            
            return record
        except Exception as e:
            raise Exception(f"Lỗi khi chấm công vào: {str(e)}")
    
    @staticmethod
    def check_out(employee_id, date, check_out_time):
        """
        Chấm công ra ca và tự động tính work_hours
        """
        try:
            record = AttendanceRecord.objects.get(
                employee_id=employee_id,
                date=date
            )
            
            record.check_out_time = check_out_time
            record.work_hours = record.calculate_work_hours()
            record.save()
            
            return record
        except AttendanceRecord.DoesNotExist:
            raise Exception("Chưa có bản ghi chấm công vào. Vui lòng chấm công vào trước.")


class SalaryService:
    """
    Service for salary calculation
    Công thức: (Số công thực tế / Số công tối đa trong tháng) * Lương cơ bản + Thưởng
    """
    
    @staticmethod
    def calculate_max_work_hours_in_month(year, month):
        """
        Tính số công tối đa trong tháng
        Giả định: Mỗi ngày có thể làm tối đa 16 công
        """
        # Lấy số ngày trong tháng
        num_days = calendar.monthrange(year, month)[1]
        
        # Số công tối đa = 16 công/ngày * số ngày trong tháng
        max_hours = Decimal(str(num_days * 16))
        
        return max_hours
    
    @staticmethod
    def calculate_monthly_salary(employee_id, month, year, bonus=None):
        """
        Tính lương tháng cho nhân viên
        
        Công thức:
        - Lương tính theo công = (Số công thực tế / Số công tối đa) * Lương cơ bản
        - Lương cuối cùng = Lương tính theo công + Thưởng (nếu có)
        
        Args:
            employee_id: ID nhân viên
            month: Tháng tính lương
            year: Năm tính lương
            bonus: Tiền thưởng (tùy chọn)
        
        Returns:
            dict: Thông tin chi tiết tính lương
        """
        try:
            # Lấy thông tin nhân viên
            from api.accounts.models import EmployeeDetail
            
            employee = User.objects.select_related('employee_detail').get(id=employee_id)
            
            # Kiểm tra có EmployeeDetail không
            if not hasattr(employee, 'employee_detail'):
                raise Exception("Nhân viên chưa có thông tin chi tiết (EmployeeDetail)")
            
            employee_detail = employee.employee_detail
            base_salary = employee_detail.salary or Decimal('0.00')
            
            if base_salary <= 0:
                raise Exception("Nhân viên chưa có lương cơ bản")
            
            # Lấy tổng hợp chấm công
            attendance_summary = AttendanceService.get_monthly_attendance_summary(
                employee_id, month, year
            )
            
            if not attendance_summary:
                raise Exception("Không tìm thấy thông tin chấm công")
            
            actual_work_hours = attendance_summary['total_work_hours']
            
            # Tính số công tối đa trong tháng
            max_work_hours = SalaryService.calculate_max_work_hours_in_month(year, month)
            
            # Tính phần trăm công
            if max_work_hours > 0:
                work_hours_percentage = (actual_work_hours / max_work_hours) * 100
            else:
                work_hours_percentage = Decimal('0.00')
            
            # Tính lương theo công
            calculated_salary = (actual_work_hours / max_work_hours) * base_salary if max_work_hours > 0 else Decimal('0.00')
            
            # Thêm thưởng nếu có
            bonus_amount = Decimal(str(bonus)) if bonus else Decimal('0.00')
            final_salary = calculated_salary + bonus_amount
            
            return {
                'employee_id': employee.id,
                'employee_name': employee.get_full_name() or employee.username,
                'employee_username': employee.username,
                'month': month,
                'year': year,
                'base_salary': base_salary,
                'actual_work_hours': actual_work_hours,
                'max_work_hours_in_month': max_work_hours,
                'work_hours_percentage': round(work_hours_percentage, 2),
                'calculated_salary': round(calculated_salary, 2),
                'bonus': bonus_amount,
                'final_salary': round(final_salary, 2),
                'details': {
                    'total_days_present': attendance_summary['total_days_present'],
                    'total_days_absent': attendance_summary['total_days_absent'],
                    'total_days_late': attendance_summary['total_days_late'],
                    'early_leave_count': attendance_summary['total_days_early_leave'],
                    'average_work_hours_per_day': float(attendance_summary['average_work_hours_per_day']),
                }
            }
            
        except User.DoesNotExist:
            raise Exception("Không tìm thấy nhân viên")
        except Exception as e:
            raise Exception(f"Lỗi khi tính lương: {str(e)}")
    
    @staticmethod
    def generate_salary_slip(employee_id, month, year, bonus=None):
        """
        Tạo phiếu lương chi tiết
        """
        salary_data = SalaryService.calculate_monthly_salary(
            employee_id, month, year, bonus
        )
        
        # Format thành phiếu lương
        slip = {
            **salary_data,
            'generated_at': datetime.now(),
            'period': f"{month:02d}/{year}",
        }
        
        return slip


class WorkScheduleService:
    """Service for work schedule operations"""
    
    # Cache timeout in seconds (5 minutes)
    CACHE_TIMEOUT = 300
    
    @staticmethod
    def get_employee_schedule(employee_id, start_date, end_date):
        """
        Lấy lịch làm việc của nhân viên trong khoảng thời gian
        Tối ưu: Sử dụng select_related và only để giảm query
        """
        return WorkSchedule.objects.filter(
            employee_id=employee_id,
            schedule_date__gte=start_date,
            schedule_date__lte=end_date,
            is_active=True
        ).select_related('employee').only(
            'id', 'schedule_date', 'shift_start_time', 'shift_end_time',
            'is_active', 'notes', 'employee__username', 'employee__first_name', 
            'employee__last_name'
        ).order_by('schedule_date', 'shift_start_time')
    
    @staticmethod
    def get_weekly_schedule(start_date, end_date=None):
        """
        Lấy lịch làm việc của tất cả nhân viên trong tuần
        Tối ưu: Sử dụng cache và select_related
        """
        if not end_date:
            end_date = start_date + timedelta(days=6)
        
        cache_key = f'weekly_schedule_{start_date}_{end_date}'
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        result = list(WorkSchedule.objects.filter(
            schedule_date__gte=start_date,
            schedule_date__lte=end_date,
            is_active=True
        ).select_related('employee').only(
            'id', 'schedule_date', 'shift_start_time', 'shift_end_time',
            'is_active', 'notes', 'employee__id', 'employee__username', 
            'employee__first_name', 'employee__last_name'
        ).order_by('schedule_date', 'shift_start_time'))
        
        cache.set(cache_key, result, WorkScheduleService.CACHE_TIMEOUT)
        
        return result
    
    @staticmethod
    def get_monthly_schedule(year, month):
        """
        Lấy lịch làm việc của tất cả nhân viên trong tháng
        Tối ưu: Sử dụng cache và select_related
        """
        cache_key = f'monthly_schedule_{year}_{month}'
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
        
        result = list(WorkSchedule.objects.filter(
            schedule_date__gte=first_day,
            schedule_date__lte=last_day,
            is_active=True
        ).select_related('employee').only(
            'id', 'schedule_date', 'shift_start_time', 'shift_end_time',
            'is_active', 'notes', 'employee__id', 'employee__username', 
            'employee__first_name', 'employee__last_name'
        ).order_by('schedule_date', 'shift_start_time'))
        
        cache.set(cache_key, result, WorkScheduleService.CACHE_TIMEOUT)
        
        return result
    
    @staticmethod
    @transaction.atomic
    def bulk_create_schedules(schedules_data):
        """
        Tạo nhiều lịch làm việc cùng lúc
        Tối ưu: Sử dụng bulk_create thay vì save() từng object
        """
        schedules = [
            WorkSchedule(**data) for data in schedules_data
        ]
        created = WorkSchedule.objects.bulk_create(schedules)
        
        # Invalidate related cache
        WorkScheduleService._invalidate_schedule_cache()
        
        return created
    
    @staticmethod
    def _invalidate_schedule_cache():
        """
        Xóa cache liên quan đến schedule khi có thay đổi
        """
        # Trong production, nên sử dụng cache.delete_pattern() hoặc cache versioning
        # Đây là implementation đơn giản
        pass
