from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from apps.laundry.models import Payment


@login_required
def payment_list(request):
    date_filter = request.GET.get('date', '')
    payments = Payment.objects.select_related('order__customer').order_by('order__order_number', 'id')

    if date_filter:
        try:
            selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            payments = payments.filter(paid_at__date=selected_date)
        except ValueError:
            pass

    total = payments.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'laundry/payments/payment_list.html', {
        'payments': payments,
        'total': total,
        'date_filter': date_filter,
    })