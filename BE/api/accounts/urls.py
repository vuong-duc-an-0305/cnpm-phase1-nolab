from django.urls import path

from .views import LoginView, LogoutView, ProfileView, RegisterView, users_list, user_detail, employee_detail

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    
    # User management (thay thế employees)
    path('users/', users_list, name='users-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    
    # Employee detail (thông tin chi tiết nhân viên)
    path('users/<int:user_id>/detail/', employee_detail, name='employee-detail'),
]
