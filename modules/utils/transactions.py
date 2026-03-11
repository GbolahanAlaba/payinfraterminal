from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime
from calendar import monthrange
from transactions.models import Transaction

class TransactionUtils:

    @staticmethod
    def success_rate_per_month(year=None):
        """
        Returns success rate per month for a given year.
        Includes all months even if there are zero transactions.
        """
        now = timezone.now()
        if year is None:
            year = now.year

        # Query transactions for the year, grouped by month
        qs = Transaction.objects.filter(
            created_at__year=year
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Count('id'),
            success=Count('id', filter=Q(status='success'))
        )

        # Convert queryset to dict for quick lookup
        month_data = {row['month'].month: row for row in qs}

        # Prepare output for all 12 months
        data = []
        for m in range(1, 13):
            row = month_data.get(m)
            total = row['total'] if row else 0
            success = row['success'] if row else 0
            success_rate = (success / total * 100) if total else 0
            data.append({
                "month": datetime(year, m, 1).strftime("%B"),
                "month_start": datetime(year, m, 1),
                "total_transactions": total,
                "successful_transactions": success,
                "success_rate": round(success_rate, 2)
            })

        return data