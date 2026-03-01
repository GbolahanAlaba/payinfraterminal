from django.db.models import F
from api.models import APIUsageRecord

def create_or_update_api_usage(client, endpoint, method, status_code, response_time):
    # Get or create the usage record
    record, created = APIUsageRecord.objects.get_or_create(
        client=client,
        endpoint=endpoint,
        defaults={
            "method": method,
            "request_count": 1,
            "status_code": status_code,
            "response_time": response_time,
        }
    )

    if not created:
        # Increment request_count and update latest status/response
        record.request_count = F("request_count") + 1
        record.status_code = status_code
        record.response_time = response_time
        record.save()
        record.refresh_from_db()  # refresh F() updates

    # # Add history entry
    # APIUsageRecordHistory.objects.create(
    #     usage_record=record,
    #     client=record.client,
    #     endpoint=record.endpoint,
    #     method=record.method,
    #     request_count=record.request_count,
    #     status_code=record.status_code,
    #     response_time=record.response_time,
    # )

    return record