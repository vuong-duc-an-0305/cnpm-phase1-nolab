"""
API URLs configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.reports.views import (
    export_report_xlsx,
    export_report_async,
    check_task_status,
    download_task_result
)

# Import routers từ các app
from api.categories.urls import router as categories_router
from api.products.urls import router as products_router
from api.ingredients.urls import router as ingredients_router
from api.recipes.urls import router as recipes_router
from api.customers.urls import router as customers_router
from api.orders.urls import router as orders_router
from api.inventory.urls import router as inventory_router
from api.employees.urls import router as employees_router

# Tạo main router
router = DefaultRouter()

# Extend router với các router con
router.registry.extend(categories_router.registry)
router.registry.extend(products_router.registry)
router.registry.extend(ingredients_router.registry)
router.registry.extend(recipes_router.registry)
router.registry.extend(customers_router.registry)
router.registry.extend(orders_router.registry)
router.registry.extend(inventory_router.registry)
router.registry.extend(employees_router.registry)

urlpatterns = [
    path('auth/', include('api.accounts.urls')),
    path('users/', include('api.accounts.urls')),  # Alias cho users management
    path('attendance/', include('api.attendance.urls')),
    path('', include(router.urls)),
    # Sync report export (original)
    path('reports/export.xlsx', export_report_xlsx),
    # Async report export (Phase 3)
    path('reports/export_async/', export_report_async, name='export_report_async'),
    path('reports/task_status/<str:task_id>/', check_task_status, name='check_task_status'),
    path('reports/download/<str:task_id>/', download_task_result, name='download_task_result'),
    # Webhooks (Phase 3)
    path('webhooks/', include('api.webhooks.urls')),
    # Real-time dashboard (Phase 4)
    path('dashboard/', include('api.realtime.urls')),
]
