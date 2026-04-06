"""
Management command to test attendance system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.attendance.models import AttendanceRecord, WorkSchedule
from api.attendance.services import AttendanceService, SalaryService
from datetime import date, time
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test attendance system functionality'

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("Testing Attendance System")
        self.stdout.write("=" * 50)
        
        try:
            # 1. Get a test user
            user = User.objects.filter(groups__name__in=['cashier', 'waiter']).first()
            if not user:
                self.stdout.write(self.style.ERROR("❌ No cashier/waiter user found. Please create one first."))
                return
            
            self.stdout.write(self.style.SUCCESS(f"✓ Test user: {user.username} (ID: {user.id})"))
            
            # 2. Test creating work schedule
            schedule, created = WorkSchedule.objects.get_or_create(
                employee=user,
                schedule_date=date.today(),
                shift_start_time=time(8, 0),
                defaults={
                    'shift_end_time': time(17, 0),
                    'is_active': True,
                    'notes': 'Test schedule'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created work schedule: {schedule}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Work schedule exists: {schedule}"))
            
            self.stdout.write(f"  - Scheduled hours: {schedule.scheduled_hours:.2f} hours")
            
            # 3. Test creating attendance record
            record, created = AttendanceRecord.objects.get_or_create(
                employee=user,
                date=date.today(),
                defaults={
                    'check_in_time': time(8, 0),
                    'check_out_time': time(17, 0),
                    'status': 'PRESENT',
                    'notes': 'Test attendance'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created attendance record: {record}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Attendance record exists: {record}"))
                
            self.stdout.write(f"  - Work hours: {record.work_hours} công")
            
            # 4. Test attendance service
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("Testing Attendance Service")
            self.stdout.write("=" * 50)
            
            summary = AttendanceService.get_monthly_attendance_summary(
                user.id,
                date.today().month,
                date.today().year
            )
            
            if summary:
                self.stdout.write(self.style.SUCCESS(f"✓ Monthly summary for {summary['employee_name']}:"))
                self.stdout.write(f"  - Month/Year: {summary['month']}/{summary['year']}")
                self.stdout.write(f"  - Total work hours: {summary['total_work_hours']} công")
                self.stdout.write(f"  - Present days: {summary['total_days_present']}")
                self.stdout.write(f"  - Absent days: {summary['total_days_absent']}")
                self.stdout.write(f"  - Late days: {summary['total_days_late']}")
            
            # 5. Test salary service (if employee has salary)
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("Testing Salary Service")
            self.stdout.write("=" * 50)
            
            try:
                if hasattr(user, 'employeedetail') and user.employeedetail.salary:
                    salary_data = SalaryService.calculate_monthly_salary(
                        user.id,
                        date.today().month,
                        date.today().year,
                        bonus=500000
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f"✓ Salary calculation for {salary_data['employee_name']}:"))
                    self.stdout.write(f"  - Base salary: {salary_data['base_salary']:,.0f} VNĐ")
                    self.stdout.write(f"  - Actual work hours: {salary_data['actual_work_hours']} công")
                    self.stdout.write(f"  - Max work hours: {salary_data['max_work_hours_in_month']} công")
                    self.stdout.write(f"  - Work percentage: {salary_data['work_hours_percentage']}%")
                    self.stdout.write(f"  - Calculated salary: {salary_data['calculated_salary']:,.0f} VNĐ")
                    self.stdout.write(f"  - Bonus: {salary_data['bonus']:,.0f} VNĐ")
                    self.stdout.write(f"  - Final salary: {salary_data['final_salary']:,.0f} VNĐ")
                else:
                    self.stdout.write(self.style.WARNING("⚠ User has no salary information. Skipping salary test."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠ Salary test failed: {str(e)}"))
            
            # 6. Test models count
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write("Database Statistics")
            self.stdout.write("=" * 50)
            
            total_schedules = WorkSchedule.objects.count()
            total_records = AttendanceRecord.objects.count()
            active_schedules = WorkSchedule.objects.filter(is_active=True).count()
            
            self.stdout.write(self.style.SUCCESS(f"✓ Total work schedules: {total_schedules}"))
            self.stdout.write(self.style.SUCCESS(f"✓ Active work schedules: {active_schedules}"))
            self.stdout.write(self.style.SUCCESS(f"✓ Total attendance records: {total_records}"))
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("✓ All tests completed successfully!"))
            self.stdout.write("=" * 50)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}"))
            import traceback
            traceback.print_exc()
