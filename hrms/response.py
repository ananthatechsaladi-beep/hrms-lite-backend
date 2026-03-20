from typing import Any, Optional

from rest_framework import status
from rest_framework.response import Response


def success_single(data: Any, status_code: int = status.HTTP_200_OK) -> Response:
    return Response({'success': True, 'data': data}, status=status_code)


def success_list(data: Any, count: Optional[int] = None, status_code: int = status.HTTP_200_OK) -> Response:
    if count is None:
        try:
            count = len(data)  # type: ignore[arg-type]
        except TypeError:
            count = None
    return Response({'success': True, 'count': count, 'data': data}, status=status_code)


def success_deleted(status_code: int = status.HTTP_200_OK) -> Response:
    # DRF default destroy returns 204; we keep a body to match your envelope format.
    return Response({'success': True, 'data': {}}, status=status_code)

