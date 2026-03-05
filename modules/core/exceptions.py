# core/exceptions.py

import uuid
import logging

from django.utils.timezone import now
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

from .error_codes import (
    INVALID_REQUEST,
    SERVER_ERROR,
)

logger = logging.getLogger(__name__)


class APIError(APIException):
    def __init__(self, message, code=None, status_code=None):
        self.status_code = status_code or 400
        self.code = code or INVALID_REQUEST

        self.detail = {
            "message": message,
            "code": self.code,
        }

        super().__init__(detail=self.detail)


def custom_exception_handler(exc, context):

    request = context.get("request")
    request_id = str(uuid.uuid4())

    response = exception_handler(exc, context)

    error_code = SERVER_ERROR


    if isinstance(exc, APIError):
        error_code = exc.code

    elif hasattr(exc, "code"):
        error_code = getattr(exc, "code", SERVER_ERROR)

    elif hasattr(exc, "default_code"):
        error_code = getattr(exc, "default_code", SERVER_ERROR)

    if response is not None:

        logger.error(
            "API Error | Path: %s | User: %s | Exception: %s",
            getattr(request, "path", "N/A"),
            getattr(request, "user", "Anonymous"),
            str(exc),
        )

        return Response(
            {
                "status": "error",
                "message": str(exc),
                "error": {
                    "code": error_code,
                    "details": response.data,
                },
                "meta": {
                    "request_id": request_id,
                    "timestamp": now(),
                },
            },
            status=response.status_code,
        )

    logger.exception("Unhandled Server Error")

    return Response(
        {
            "status": "error",
            "message": "Internal server error",
            "error": {
                "code": SERVER_ERROR,
                "details": "An unexpected error occurred.",
            },
            "meta": {
                "request_id": request_id,
                "timestamp": now(),
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )