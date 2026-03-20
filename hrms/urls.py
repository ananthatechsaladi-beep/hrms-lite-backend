from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceByRangeView,
    AttendanceSummaryView,
    AttendanceViewSet,
    EmployeeViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = router.urls + [
    path('reports/attendance-summary', AttendanceSummaryView.as_view(), name='attendance-summary'),
    path('reports/attendance-by-range', AttendanceByRangeView.as_view(), name='attendance-by-range'),
]

