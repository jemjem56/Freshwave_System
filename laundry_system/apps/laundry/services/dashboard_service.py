import json
from datetime import date, timedelta
from django.db.models import Sum
from apps.laundry.models import Customer, Order, Payment, Notification


def get_dashboard_context():
    today = date.today()

    status_counts = {
        'received': Order.objects.filter(status='received').count(),
        'washing': Order.objects.filter(status='washing').count(),
        'drying': Order.objects.filter(status='drying').count(),
        'folding': Order.objects.filter(status='folding').count(),
        'ready': Order.objects.filter(status='ready').count(),
    }

    weekly_revenue = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        revenue = Payment.objects.filter(
            paid_at__date=day,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

        weekly_revenue.append({
            'day': day.strftime('%a'),
            'amount': float(revenue),
        })

    notifications = Notification.objects.filter(is_read=False)[:5]

    return {
        'total_customers': Customer.objects.count(),
        'active_orders': Order.objects.exclude(status__in=['completed', 'cancelled']).count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'today_revenue': Payment.objects.filter(
            paid_at__date=today,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'recent_orders': Order.objects.select_related('customer').order_by('order_number')[:8],
        'notifications': notifications,
        'unread_count': notifications.count(),
        'status_counts': status_counts,
        'weekly_revenue': json.dumps(weekly_revenue),
    }