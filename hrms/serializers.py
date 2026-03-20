import uuid as uuidlib

from rest_framework import serializers

from .models import Attendance, Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',
            'full_name',
            'email',
            'department',
            'created_at',
            'updated_at',
        ]


class AttendanceCreateSerializer(serializers.ModelSerializer):
    # The UI may send either `Employee.id` (UUID) OR `Employee.employee_id` (code like EMP01).
    employee_id = serializers.CharField()

    class Meta:
        model = Attendance
        fields = [
            'id',
            'employee_id',
            'date',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        raw_employee_id = attrs.get('employee_id')
        if raw_employee_id is None:
            raise serializers.ValidationError({'employee_id': 'This field is required.'})

        employee = self._resolve_employee(raw_employee_id)
        attrs['employee'] = employee
        return attrs

    def _resolve_employee(self, raw_employee_id: str) -> Employee:
        # 1) Try UUID (Employee.id)
        try:
            as_uuid = uuidlib.UUID(str(raw_employee_id))
            return Employee.objects.get(id=as_uuid)
        except (ValueError, Employee.DoesNotExist):
            pass

        # 2) Try employee code (Employee.employee_id like EMP01)
        try:
            return Employee.objects.get(employee_id=str(raw_employee_id))
        except Employee.DoesNotExist as exc:
            raise serializers.ValidationError('Employee not found for the given employee_id.') from exc

    def create(self, validated_data):
        employee = validated_data.pop('employee')
        validated_data.pop('employee_id', None)  # remove the raw input
        return Attendance.objects.create(employee=employee, **validated_data)


class AttendanceDetailSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.id', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'employee_id',
            'date',
            'status',
            'created_at',
            'updated_at',
        ]


class AttendanceStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Attendance.Status.choices)

    class Meta:
        model = Attendance
        fields = ['status']

