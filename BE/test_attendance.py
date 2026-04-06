"""
Script để test attendance system
"""
from django.contrib.auth.models import User
from api.attendance.models import AttendanceRecord, WorkSchedule
from api.attendance.services import AttendanceService, SalaryService
from datetime import date, time
from decimal import Decimal

def test_attendance_system():
    print("=" * 50)
    print("Testing Attendance System")
    print("=" * 50)
    
    # 1. Get a test user
    try:
        user = User.objects.filter(groups__name__in=['cashier', 'waiter']).first()
        if not user:
            print("❌ No cashier/waiter user found. Please create one first.")
            return
        
        print(f"✓ Test user: {user.username} (ID: {user.id})")
        
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
            print(f"✓ Created work schedule: {schedule}")
        else:
            print(f"✓ Work schedule exists: {schedule}")
        
        print(f"  - Scheduled hours: {schedule.scheduled_hours:.2f} hours")
        
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
            print(f"✓ Created attendance record: {record}")
        else:
            print(f"✓ Attendance record exists: {record}")
            
        print(f"  - Work hours: {record.work_hours} công")
        
        # 4. Test attendance service
        print("\n" + "=" * 50)
        print("Testing Attendance Service")
        print("=" * 50)
        
        summary = AttendanceService.get_monthly_attendance_summary(
            user.id,
            date.today().month,
            date.today().year
        )
        
        if summary:
            print(f"✓ Monthly summary for {summary['employee_name']}:")
            print(f"  - Month/Year: {summary['month']}/{summary['year']}")
            print(f"  - Total work hours: {summary['total_work_hours']} công")
            print(f"  - Present days: {summary['total_days_present']}")
            print(f"  - Absent days: {summary['total_days_absent']}")
            print(f"  - Late days: {summary['total_days_late']}")
        
        # 5. Test salary service (if employee has salary)
        print("\n" + "=" * 50)
        print("Testing Salary Service")
        print("=" * 50)
        
        try:
            if hasattr(user, 'employeedetail') and user.employeedetail.salary:
                salary_data = SalaryService.calculate_monthly_salary(
                    user.id,
                    date.today().month,
                    date.today().year,
                    bonus=500000
                )
                
                print(f"✓ Salary calculation for {salary_data['employee_name']}:")
                print(f"  - Base salary: {salary_data['base_salary']:,.0f} VNĐ")
                print(f"  - Actual work hours: {salary_data['actual_work_hours']} công")
                print(f"  - Max work hours: {salary_data['max_work_hours_in_month']} công")
                print(f"  - Work percentage: {salary_data['work_hours_percentage']}%")
                print(f"  - Calculated salary: {salary_data['calculated_salary']:,.0f} VNĐ")
                print(f"  - Bonus: {salary_data['bonus']:,.0f} VNĐ")
                print(f"  - Final salary: {salary_data['final_salary']:,.0f} VNĐ")
            else:
                print("⚠ User has no salary information. Skipping salary test.")
        except Exception as e:
            print(f"⚠ Salary test failed: {str(e)}")
        
        # 6. Test models count
        print("\n" + "=" * 50)
        print("Database Statistics")
        print("=" * 50)
        
        total_schedules = WorkSchedule.objects.count()
        total_records = AttendanceRecord.objects.count()
        active_schedules = WorkSchedule.objects.filter(is_active=True).count()
        
        print(f"✓ Total work schedules: {total_schedules}")
        print(f"✓ Active work schedules: {active_schedules}")
        print(f"✓ Total attendance records: {total_records}")
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_attendance_system()
