from apps.laundry.models import Notification
from apps.laundry.notifications import (
    notify_order_ready,
    notify_order_received,
    notify_order_completed,
)


def update_order_status(order, status_form):
    old_status = order.status
    updated_order = status_form.save()

    Notification.objects.create(
        order=updated_order,
        title=f'Order #{updated_order.order_number} Status Updated',
        message=f'{updated_order.customer.name}\'s order is now "{updated_order.get_status_display()}".',
        type='status',
    )

    if updated_order.status == 'ready' and old_status != 'ready':
        Notification.objects.create(
            order=updated_order,
            title=f'Order #{updated_order.order_number} Ready for Pickup',
            message=f'{updated_order.customer.name}\'s laundry is ready! Call {updated_order.customer.phone}.',
            type='ready',
        )
        notify_order_ready(updated_order)

    if updated_order.status == 'received' and old_status != 'received':
        notify_order_received(updated_order)

    if updated_order.status == 'completed' and old_status != 'completed':
        notify_order_completed(updated_order)

    return updated_order