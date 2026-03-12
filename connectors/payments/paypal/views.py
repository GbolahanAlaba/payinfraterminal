"""
DRF views for PayPal Checkout (Orders v2) and Webhooks.
"""
from __future__ import annotations

import logging
import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .client import paypal_client
from .base import Money, OrderItem, OrderRequest
from .exceptions import PayPalAuthError, PayPalError, PayPalWebhookError
from .serializers import CreateOrderSerializer, RefundSerializer
from .webhook import dispatch

logger = logging.getLogger(__name__)


def _idempotency_key(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, ":".join(parts)))


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class CreateOrderView(APIView):
    """
    POST /api/payments/paypal/orders/

    Creates a PayPal order and returns the order ID + buyer approval URL.
    The frontend passes the order ID to the PayPal JS SDK.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        items = [
            OrderItem(
                name=i["name"],
                unit_amount=Money(i["unit_amount"]["currency_code"], i["unit_amount"]["value"]),
                quantity=i["quantity"],
                description=i.get("description", ""),
                sku=i.get("sku", ""),
                category=i.get("category", "PHYSICAL_GOODS"),
            )
            for i in data.get("items", [])
        ]
        order_request = OrderRequest(
            intent=data["intent"],
            currency_code=data["currency_code"],
            total_amount=data["total_amount"],
            items=items,
            custom_id=data.get("custom_id", ""),
            invoice_id=data.get("invoice_id", ""),
            description=data.get("description", ""),
            return_url=data.get("return_url", ""),
            cancel_url=data.get("cancel_url", ""),
            shipping_preference=data.get("shipping_preference", "NO_SHIPPING"),
        )
        idem_key = _idempotency_key(
            str(request.user.pk),
            data.get("invoice_id") or data.get("custom_id") or str(uuid.uuid4()),
        )
        try:
            order = paypal_client.create_order(order_request, idempotency_key=idem_key)
        except PayPalAuthError as exc:
            logger.error("PayPal auth error: %s", exc)
            return Response(
                {"error": "Payment provider authentication failed. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except PayPalError as exc:
            logger.error("PayPal create_order error: %s | details=%s", exc, exc.details)
            return Response(
                {"error": "Could not create payment order.", "details": exc.details},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        approval_url = next(
            (link["href"] for link in order.get("links", []) if link.get("rel") == "approve"),
            None,
        )
        return Response(
            {
                "paypal_order_id": order["id"],
                "status": order.get("status"),
                "approval_url": approval_url,
            },
            status=status.HTTP_201_CREATED,
        )


class GetOrderView(APIView):
    """GET /api/payments/paypal/orders/<paypal_order_id>/"""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, paypal_order_id: str) -> Response:
        try:
            order = paypal_client.get_order(paypal_order_id)
        except PayPalError as exc:
            return Response(
                {"error": "Could not retrieve order.", "details": exc.details},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(order)


class CaptureOrderView(APIView):
    """
    POST /api/payments/paypal/orders/<paypal_order_id>/capture/

    Called after the buyer approves on PayPal. Idempotent.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, paypal_order_id: str) -> Response:
        idem_key = _idempotency_key(str(request.user.pk), paypal_order_id, "capture")
        try:
            result = paypal_client.capture_order(paypal_order_id, idempotency_key=idem_key)
        except PayPalError as exc:
            logger.error("Capture failed order=%s: %s | details=%s", paypal_order_id, exc, exc.details)
            return Response(
                {"error": "Payment capture failed.", "details": exc.details},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        purchase_units = result.get("purchase_units", [])
        captures = purchase_units[0].get("payments", {}).get("captures", []) if purchase_units else []
        capture_id = captures[0].get("id") if captures else None

        return Response({
            "paypal_order_id": result.get("id"),
            "status": result.get("status"),
            "capture_id": capture_id,
        })


# ---------------------------------------------------------------------------
# Refunds
# ---------------------------------------------------------------------------

class RefundView(APIView):
    """
    POST /api/payments/paypal/refunds/

    Issue a full or partial refund on a captured payment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = RefundSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        amount: Money | None = None
        if data.get("amount"):
            a = data["amount"]
            amount = Money(a["currency_code"], a["value"])

        try:
            result = paypal_client.refund_capture(
                capture_id=data["capture_id"],
                amount=amount,
                note_to_payer=data.get("note_to_payer", ""),
                invoice_id=data.get("invoice_id", ""),
            )
        except PayPalError as exc:
            logger.error("Refund failed capture=%s: %s", data["capture_id"], exc)
            return Response(
                {"error": "Refund failed.", "details": exc.details},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"refund_id": result.get("id"), "status": result.get("status")})


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

class WebhookView(APIView):
    """
    POST /api/payments/paypal/webhook/

    Receives and verifies PayPal webhook events.
    Auth is via PayPal's own signature — NOT session/token auth.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request) -> Response:
        h = request.headers
        try:
            verified = paypal_client.verify_signature(
                transmission_id=h.get("PayPal-Transmission-Id", ""),
                timestamp=h.get("PayPal-Transmission-Time", ""),
                cert_url=h.get("PayPal-Cert-Url", ""),
                auth_algo=h.get("PayPal-Auth-Algo", ""),
                actual_sig=h.get("PayPal-Transmission-Sig", ""),
                body=request.body,
            )
        except PayPalWebhookError as exc:
            logger.error("Webhook config error: %s", exc)
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not verified:
            logger.warning("Invalid PayPal webhook signature")
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        event = request.data
        event_type = event.get("event_type", "")
        resource = event.get("resource", {})
        logger.info("PayPal webhook: %s id=%s", event_type, event.get("id"))

        try:
            dispatch(event_type=event_type, resource=resource, raw_event=event)
        except Exception as exc:  # noqa: BLE001
            # Never return 5xx to PayPal — it would trigger endless retries
            logger.exception("Unhandled error in webhook handler for %s: %s", event_type, exc)

        return Response({"status": "ok"})
