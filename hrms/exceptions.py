from __future__ import annotations

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def _normalize_error(detail):
    """
    Convert DRF error objects into the API's `error` field.
    """
    if isinstance(detail, dict) or isinstance(detail, list):
        return detail
    return str(detail)


def exception_handler(exc, context): 
    if isinstance(exc, IntegrityError):
        return Response(
            {'success': False, 'error': 'Duplicate value. Please check unique constraints.'},
            status=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, ValidationError):
        return Response(
            {'success': False, 'error': exc.detail},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        return Response(
            {'success': False, 'error': _normalize_error(response.data)},
            status=response.status_code,
        )

    return Response(
        {'success': False, 'error': str(exc)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

