from decimal import Decimal

from apps.laundry.models import Notification
from apps.laundry.notifications import notify_payment_received


def record_order_payment(order, payment_form):
    payment = payment_form.save(commit=False)
    payment.order = order

    if payment.amount is None or payment.amount <= Decimal("0.00"):
        raise ValueError("Payment amount must be greater than 0.")

    new_total_paid = order.amount_paid + payment.amount

    if new_total_paid >= order.total_amount:
        payment.status = 'paid'
    elif new_total_paid > 0:
        payment.status = 'partial'
    else:
        payment.status = 'pending'

    payment.save()
    order.refresh_from_db()

    Notification.objects.create(
        order=order,
        title=f'Payment Recorded — Order #{order.order_number}',
        message=f'₱{payment.amount:.2f} via {payment.get_method_display()} recorded for {order.customer.name}. Balance: ₱{order.balance:.2f}',
        type='payment',
    )

    notify_payment_received(order, payment)

    return payment