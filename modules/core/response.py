

from rest_framework.response import Response
from django.utils.timezone import now
import uuid


def success_response(data=None, message="Request successful", status_code=200):
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data,
            "meta": {
                "request_id": str(uuid.uuid4()),
                "timestamp": now(),
            },
        },
        status=status_code,
    )


def error_response(
    message="Request failed",
    errors=None,
    status_code=400,
):
    return Response(
        {
            "status": "error",
            "message": message,
            "errors": errors,
            "meta": {
                "request_id": str(uuid.uuid4()),
                "timestamp": now(),
            },
        },
        status=status_code,
    )