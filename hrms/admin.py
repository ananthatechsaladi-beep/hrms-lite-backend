from django.contrib import admin

from .models import Attendance, Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'email', 'department', 'created_at')
    search_fields = ('employee_id', 'full_name', 'email', 'department')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'date', 'status', 'created_at')
    search_fields = ('employee__employee_id', 'employee__full_name')
    list_filter = ('date', 'status', 'employee__department')
