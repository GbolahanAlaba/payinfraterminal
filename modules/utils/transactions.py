from django.db.models import Count, Q
from django.db.models.functions import TruncHour
from datetime import timedelta
from django.utils import timezone
from transactions.models import Transaction, TransactionAttempt


class TransactionUtils:

    @staticmethod
    # def success_rate_per_4hours(provider_name):
    def success_rate_per_4hours():
        now = timezone.now()
        start = now - timedelta(days=1)
        
        qs = Transaction.objects.filter(
            created_at__gte=start
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            total=Count('id'),
            success=Count('id', filter=Q(status='success'))
        ).order_by('hour')
        
        data = []
        interval_start = None
        interval_total = 0
        interval_success = 0
        
        for i, row in enumerate(qs):
            hour = row['hour']
            if interval_start is None:
                interval_start = hour
            # Check if current hour is 4 hours after interval start
            if (hour - interval_start).total_seconds() >= 4*3600:
                # save previous interval
                success_rate = (interval_success/interval_total*100) if interval_total else 0
                data.append({
                    "interval_start": interval_start,
                    "interval_end": hour,
                    "success_rate": round(success_rate, 2)
                })
                # reset counters
                interval_start = hour
                interval_total = row['total']
                interval_success = row['success']
            else:
                interval_total += row['total']
                interval_success += row['success']
        
        # Last interval
        if interval_total:
            success_rate = (interval_success/interval_total*100)
            data.append({
                "interval_start": interval_start,
                "interval_end": hour,
                "success_rate": round(success_rate, 2)
            })
        
        return data