"""
Views for Attendance Management API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import calendar

from .models import AttendanceRecord, WorkSchedule
from .serializers import (
    AttendanceRecordSerializer,
    WorkScheduleSerializer,
    AttendanceSummarySerializer,
    SalaryCalculationSerializer,
)
from .services import AttendanceService, SalaryService, WorkScheduleService
from api.core.permissions import IsAdminOrCashierRole


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance records
    
    list: Lấy danh sách bản ghi chấm công
    create: Tạo bản ghi chấm công mới
    retrieve: Xem chi tiết bản ghi chấm công
    update: Cập nhật bản ghi chấm công
    partial_update: Cập nhật một phần bản ghi chấm công
    destroy: Xóa bản ghi chấm công
    """
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'date', 'status']
    search_fields = ['employee__username', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['date', 'check_in_time', 'work_hours']
    ordering = ['-date']

    def get_queryset(self):
        """
        Filter queryset based on user role
        Tối ưu: Sử dụng select_related và only để giảm dữ liệu truyền tải
        """
        queryset = super().get_queryset().select_related(
            'employee',
            'approved_by'
        ).only(
            'id', 'date', 'check_in_time', 'check_out_time', 'work_hours', 
            'status', 'notes', 'approved_at', 'created_at', 'updated_at',
            'employee__id', 'employee__username', 'employee__first_name', 'employee__last_name',
            'approved_by__id', 'approved_by__username'
        )
        
        # Nếu không phải admin/manager, chỉ xem được attendance của mình
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def check_in(self, request):
        """
        Chấm công vào ca
        
        POST /api/attendance/records/check_in/
        Body: {
            "employee": 1,
            "date": "2024-01-15",
            "check_in_time": "08:00:00",
            "notes": "Optional notes"
        }
        """
        employee_id = request.data.get('employee')
        date_str = request.data.get('date')
        check_in_time_str = request.data.get('check_in_time')
        notes = request.data.get('notes')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            check_in_time = datetime.strptime(check_in_time_str, '%H:%M:%S').time()
            
            record = AttendanceService.check_in(
                employee_id, date, check_in_time, notes
            )
            
            serializer = self.get_serializer(record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def check_out(self, request):
        """
        Chấm công ra ca
        
        POST /api/attendance/records/check_out/
        Body: {
            "employee": 1,
            "date": "2024-01-15",
            "check_out_time": "17:00:00"
        }
        """
        employee_id = request.data.get('employee')
        date_str = request.data.get('date')
        check_out_time_str = request.data.get('check_out_time')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            check_out_time = datetime.strptime(check_out_time_str, '%H:%M:%S').time()
            
            record = AttendanceService.check_out(
                employee_id, date, check_out_time
            )
            
            serializer = self.get_serializer(record)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Tổng hợp chấm công theo tháng
        
        GET /api/attendance/records/summary/?employee=1&month=1&year=2024
        """
        employee_id = request.query_params.get('employee')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not all([employee_id, month, year]):
            return Response(
                {'error': 'Cần cung cấp employee, month và year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            summary = AttendanceService.get_monthly_attendance_summary(
                int(employee_id), int(month), int(year)
            )
            
            if not summary:
                return Response(
                    {'error': 'Không tìm thấy dữ liệu'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = AttendanceSummarySerializer(summary)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def approve(self, request, pk=None):
        """
        Phê duyệt bản ghi chấm công
        
        POST /api/attendance/records/{id}/approve/
        """
        record = self.get_object()
        
        record.approved_by = request.user
        record.approved_at = timezone.now()
        record.save(update_fields=['approved_by', 'approved_at', 'updated_at'])
        
        serializer = self.get_serializer(record)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def quick_check_in(self, request, pk=None):
        """
        Chấm công vào ca nhanh từ attendance record
        
        POST /api/attendance/records/{id}/quick_check_in/
        Body: {
            "check_in_time": "08:30:00"  # Optional, default to now
        }
        """
        record = self.get_object()
        
        if record.check_in_time:
            return Response(
                {'error': 'Đã chấm công vào ca rồi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        check_in_time_str = request.data.get('check_in_time')
        
        if check_in_time_str:
            check_in_time = datetime.strptime(check_in_time_str, '%H:%M:%S').time()
        else:
            check_in_time = timezone.localtime(timezone.now()).time()
        
        record.check_in_time = check_in_time
        record.status = 'PRESENT'
        record.save(update_fields=['check_in_time', 'status', 'updated_at'])
        
        serializer = self.get_serializer(record)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def quick_check_out(self, request, pk=None):
        """
        Kết ca nhanh từ attendance record
        
        POST /api/attendance/records/{id}/quick_check_out/
        Body: {
            "check_out_time": "17:30:00"  # Optional, default to now
        }
        """
        record = self.get_object()
        
        if not record.check_in_time:
            return Response(
                {'error': 'Chưa chấm công vào ca'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if record.check_out_time:
            return Response(
                {'error': 'Đã kết ca rồi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        check_out_time_str = request.data.get('check_out_time')
        
        if check_out_time_str:
            check_out_time = datetime.strptime(check_out_time_str, '%H:%M:%S').time()
        else:
            check_out_time = timezone.localtime(timezone.now()).time()
        
        record.check_out_time = check_out_time
        record.save()  # Will auto-calculate work_hours
        
        serializer = self.get_serializer(record)
        return Response(serializer.data)


class WorkScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing work schedules
    
    list: Lấy danh sách lịch làm việc
    create: Tạo lịch làm việc mới
    retrieve: Xem chi tiết lịch làm việc
    update: Cập nhật lịch làm việc
    partial_update: Cập nhật một phần lịch làm việc
    destroy: Xóa lịch làm việc
    """
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'schedule_date', 'is_active']
    search_fields = ['employee__username', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['schedule_date', 'shift_start_time']
    ordering = ['schedule_date', 'shift_start_time']

    def get_queryset(self):
        """
        Filter queryset based on user role and query params
        Tối ưu: Sử dụng select_related và only để giảm dữ liệu truyền tải
        """
        queryset = super().get_queryset().select_related('employee').only(
            'id', 'schedule_date', 'shift_start_time', 'shift_end_time',
            'is_active', 'notes', 'created_at', 'updated_at',
            'employee__id', 'employee__username', 'employee__first_name', 'employee__last_name'
        )
        
        # Nếu không phải admin/manager, chỉ xem được schedule của mình
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(schedule_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(schedule_date__lte=end_date)
        
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        """Tạo schedule mới với transaction"""
        serializer.save()

    @transaction.atomic
    def perform_update(self, serializer):
        """Cập nhật schedule với transaction"""
        serializer.save()

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_create(self, request):
        """
        Tạo nhiều lịch làm việc cùng lúc
        
        POST /api/attendance/schedules/bulk_create/
        Body: [
            {"employee": 1, "schedule_date": "2024-01-15", "shift_start_time": "08:00:00", "shift_end_time": "17:00:00"},
            {"employee": 2, "schedule_date": "2024-01-15", "shift_start_time": "08:00:00", "shift_end_time": "17:00:00"}
        ]
        """
        schedules_data = request.data
        
        if not isinstance(schedules_data, list):
            return Response(
                {'error': 'Dữ liệu phải là một danh sách'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validate all schedules first
            serializers = []
            for data in schedules_data:
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializers.append(serializer)
            
            # Create all schedules
            created_schedules = []
            for serializer in serializers:
                created_schedules.append(serializer.save())
            
            result_serializer = self.get_serializer(created_schedules, many=True)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        """
        Lấy lịch làm việc theo tuần hoặc khoảng thời gian tùy chỉnh
        
        GET /api/attendance/schedules/weekly/?start_date=2024-01-15
        GET /api/attendance/schedules/weekly/?start_date=2024-01-15&end_date=2024-01-21
        Hoặc GET /api/attendance/schedules/weekly/ (lấy tuần hiện tại)
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            # Lấy ngày đầu tuần hiện tại (Monday)
            today = datetime.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = start_date + timedelta(days=6)
        
        schedules = WorkScheduleService.get_weekly_schedule(start_date, end_date)
        
        # Nếu không phải admin/manager, chỉ lấy schedule của mình
        if not request.user.is_staff:
            schedules = schedules.filter(employee=request.user)
        
        serializer = self.get_serializer(schedules, many=True)
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'schedules': serializer.data
        })

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """
        Lấy lịch làm việc theo tháng
        
        GET /api/attendance/schedules/monthly/?month=1&year=2024
        Hoặc GET /api/attendance/schedules/monthly/ (lấy tháng hiện tại)
        """
        month_str = request.query_params.get('month')
        year_str = request.query_params.get('year')
        
        if month_str and year_str:
            month = int(month_str)
            year = int(year_str)
        else:
            today = datetime.now()
            month = today.month
            year = today.year
        
        schedules = WorkScheduleService.get_monthly_schedule(year, month)
        
        # Nếu không phải admin/manager, chỉ lấy schedule của mình
        if not request.user.is_staff:
            schedules = schedules.filter(employee=request.user)
        
        serializer = self.get_serializer(schedules, many=True)
        return Response({
            'month': month,
            'year': year,
            'schedules': serializer.data
        })


class SalaryViewSet(viewsets.ViewSet):
    """
    ViewSet for salary calculations
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def calculate(self, request):
        """
        Tính lương cho nhân viên
        
        GET /api/attendance/salary/calculate/?employee=1&month=1&year=2024&bonus=1000000
        """
        employee_id = request.query_params.get('employee')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        bonus = request.query_params.get('bonus', 0)
        
        if not all([employee_id, month, year]):
            return Response(
                {'error': 'Cần cung cấp employee, month và year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            salary_data = SalaryService.calculate_monthly_salary(
                int(employee_id),
                int(month),
                int(year),
                float(bonus) if bonus else None
            )
            
            serializer = SalaryCalculationSerializer(salary_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def slip(self, request):
        """
        Tạo phiếu lương
        
        GET /api/attendance/salary/slip/?employee=1&month=1&year=2024&bonus=1000000
        """
        employee_id = request.query_params.get('employee')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        bonus = request.query_params.get('bonus', 0)
        
        if not all([employee_id, month, year]):
            return Response(
                {'error': 'Cần cung cấp employee, month và year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            slip = SalaryService.generate_salary_slip(
                int(employee_id),
                int(month),
                int(year),
                float(bonus) if bonus else None
            )
            
            return Response(slip)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
