from __future__ import annotations

from typing import Any, Tuple

import uuid as uuidlib

from django.db.models import Case, Count, IntegerField, When
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance, Employee
from .response import success_list
from .serializers import (
    AttendanceCreateSerializer,
    AttendanceDetailSerializer,
    AttendanceStatusUpdateSerializer,
    EmployeeSerializer,
)


class EnvelopeModelViewSet(viewsets.ModelViewSet):
    """
    Wrap all list/retrieve/create/update/destroy responses to match:
      { "success": true, "data": ... } and list variants with `count`.
    """

    def _unwrap_list(self, response_data: Any) -> Tuple[Any, Any]:
        # If pagination is enabled later, DRF uses {'count': X, 'results': [...]}
        if isinstance(response_data, dict) and 'results' in response_data:
            return response_data.get('results', []), response_data.get('count', None)
        return response_data, None

    def list(self, request, *args, **kwargs):  # type: ignore[override]
        resp = super().list(request, *args, **kwargs)
        data, count = self._unwrap_list(resp.data)
        return Response({'success': True, 'count': count if count is not None else len(data), 'data': data}, status=resp.status_code)

    def retrieve(self, request, *args, **kwargs):  # type: ignore[override]
        resp = super().retrieve(request, *args, **kwargs)
        return Response({'success': True, 'data': resp.data}, status=resp.status_code)

    def create(self, request, *args, **kwargs):  # type: ignore[override]
        resp = super().create(request, *args, **kwargs)
        return Response({'success': True, 'data': resp.data}, status=resp.status_code)

    def update(self, request, *args, **kwargs):  # type: ignore[override]
        resp = super().update(request, *args, **kwargs)
        return Response({'success': True, 'data': resp.data}, status=resp.status_code)

    def destroy(self, request, *args, **kwargs):  # type: ignore[override]
        super().destroy(request, *args, **kwargs)
        return Response({'success': True, 'data': {}}, status=status.HTTP_200_OK)


class EmployeeViewSet(EnvelopeModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all().order_by('-created_at')

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        department = self.request.query_params.get('department')
        if department:
            qs = qs.filter(department=department)
        return qs


class AttendanceViewSet(EnvelopeModelViewSet):
    queryset = Attendance.objects.select_related('employee').all().order_by('-date', '-created_at')
    serializer_class = AttendanceDetailSerializer

    def get_serializer_class(self):  # type: ignore[override]
        if self.action == 'create':
            return AttendanceCreateSerializer
        if self.action in {'update', 'partial_update'}:
            return AttendanceStatusUpdateSerializer
        return AttendanceDetailSerializer

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        params = self.request.query_params

        employee_id = params.get('employee_id')
        if employee_id:
            # UI might pass employee code (EMP01) instead of UUID.
            try:
                as_uuid = uuidlib.UUID(str(employee_id))
                qs = qs.filter(employee__id=as_uuid)
            except ValueError:
                qs = qs.filter(employee__employee_id=employee_id)

        date = params.get('date')
        if date:
            parsed = parse_date(date)
            if parsed is None:
                raise ValidationError({'date': 'Invalid date format. Use YYYY-MM-DD.'})
            qs = qs.filter(date=parsed)

        start_date = params.get('start_date')
        end_date = params.get('end_date')
        if start_date or end_date:
            if not start_date or not end_date:
                raise ValidationError({'range': 'Both start_date and end_date are required.'})
            start = parse_date(start_date)
            end = parse_date(end_date)
            if start is None or end is None:
                raise ValidationError({'range': 'Invalid date format. Use YYYY-MM-DD.'})
            qs = qs.filter(date__range=(start, end))

        status_value = params.get('status')
        if status_value:
            if status_value not in {c[0] for c in Attendance.Status.choices}:
                raise ValidationError({'status': 'Status must be Present or Absent.'})
            qs = qs.filter(status=status_value)

        return qs


class AttendanceSummaryView(APIView):
    def get(self, request):  # type: ignore[override]
        department = request.query_params.get('department')

        qs = Attendance.objects.select_related('employee')
        if department:
            qs = qs.filter(employee__department=department)

        aggregated = (
            qs.values(
                'employee__id',
                'employee__employee_id',
                'employee__full_name',
                'employee__department',
            )
            .annotate(
                present_count=Count(
                    Case(
                        When(status=Attendance.Status.PRESENT, then=1),
                        output_field=IntegerField(),
                    )
                ),
                absent_count=Count(
                    Case(
                        When(status=Attendance.Status.ABSENT, then=1),
                        output_field=IntegerField(),
                    )
                ),
            )
            .order_by('employee__employee_id')
        )

        data = [
            {
                'employee_id': str(row['employee__id']),
                'full_name': row['employee__full_name'],
                'department': row['employee__department'],
                'present_count': row['present_count'],
                'absent_count': row['absent_count'],
            }
            for row in aggregated
        ]
        return Response({'success': True, 'count': len(data), 'data': data}, status=status.HTTP_200_OK)


class AttendanceByRangeView(APIView):
    def get(self, request):  # type: ignore[override]
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not start_date or not end_date:
            raise ValidationError({'range': 'start_date and end_date are required.'})

        start = parse_date(start_date)
        end = parse_date(end_date)
        if start is None or end is None:
            raise ValidationError({'range': 'Invalid date format. Use YYYY-MM-DD.'})

        qs = (
            Attendance.objects.select_related('employee')
            .filter(date__range=(start, end))
            .order_by('date', 'employee__employee_id')
        )

        data = [
            {
                'id': str(a.id),
                'employee_id': str(a.employee.id),
                'date': a.date.isoformat(),
                'status': a.status,
                'employee_full_name': a.employee.full_name,
                'department': a.employee.department,
            }
            for a in qs
        ]
        return Response({'success': True, 'count': len(data), 'data': data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def api_root(request):  # type: ignore[override]
    data = {
        'endpoints': [
            {'method': 'GET', 'path': '/health'},
            {'method': 'GET', 'path': '/api/employees'},
            {'method': 'POST', 'path': '/api/employees'},
            {'method': 'GET', 'path': '/api/employees/{id}'},
            {'method': 'PUT', 'path': '/api/employees/{id}'},
            {'method': 'DELETE', 'path': '/api/employees/{id}'},
            {'method': 'GET', 'path': '/api/attendance'},
            {'method': 'POST', 'path': '/api/attendance'},
            {'method': 'GET', 'path': '/api/attendance/{id}'},
            {'method': 'PUT', 'path': '/api/attendance/{id}'},
            {'method': 'DELETE', 'path': '/api/attendance/{id}'},
            {'method': 'GET', 'path': '/api/reports/attendance-summary'},
            {'method': 'GET', 'path': '/api/reports/attendance-by-range'},
        ],
        'docs': {
            'swagger_ui': '/docs/',
            'schema': '/api/schema/',
        },
    }
    return Response({'success': True, 'data': data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def health(request):  # type: ignore[override]
    return Response({'success': True, 'data': {'status': 'ok'}}, status=status.HTTP_200_OK)

