"""
URL routing for Attendance API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceRecordViewSet, WorkScheduleViewSet, SalaryViewSet

router = DefaultRouter()
router.register(r'records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'schedules', WorkScheduleViewSet, basename='work-schedule')
router.register(r'salary', SalaryViewSet, basename='salary')

urlpatterns = [
    path('', include(router.urls)),
]
