"""
Realtime API URLs
Phase 4: Dashboard real-time stats
"""
from django.urls import path
from . import views

urlpatterns = [
    path('realtime-stats/', views.dashboard_realtime_stats, name='dashboard_realtime_stats'),
]
