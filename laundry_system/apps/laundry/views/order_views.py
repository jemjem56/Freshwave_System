from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.laundry.forms import OrderForm, OrderStatusForm, PaymentForm, ServiceSelectionForm
from apps.laundry.models import Customer, Order, OrderItem, Service, Notification
from apps.laundry.serializers import CustomerSerializer
from apps.laundry.services.payment_service import record_order_payment
from apps.laundry.services.order_service import update_order_status
from apps.laundry.notifications import (
    send_sms,
    send_email,
    notify_order_received,
)

@login_required
def order_list(request):
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()
    
    orders = Order.objects.select_related('customer').order_by('order_number')

    if status_filter:
        orders = orders.filter(status=status_filter)

    if q:
        orders = orders.filter(
            Q(customer__name__icontains=q) |
            Q(order_number__icontains=q)
        )

        if q.isdigit():
            orders = (orders | Order.objects.filter(order_number=int(q))).distinct()
    
    status_choices = Order.STATUS_CHOICES
    all_customers = list(
        Customer.objects.order_by('name').values_list('name', flat=True)
    )
    return render(request, 'laundry/orders/order_list.html', {
        'orders': orders, 'status_filter': status_filter,
        'status_choices': status_choices, 'query': q,
        'all_customer_names': all_customers,
    })

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    status_form = OrderStatusForm(instance=order)
    payment_form = PaymentForm()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        # 🔔 NEW: SEND NOTIFICATION BUTTON
        if action == "send_notification":
            customer = order.customer
            sms_message = (
                f"Hello {customer.name}, your laundry #{order.order_number} "
                f"is {order.get_status_display()}. \n"
                f" Tracking Number: {order.tracking_id} "
                f"Balance: PHP {order.balance:.2f}. Thank you!"
            )
            # ✅ SEND SMS
            if customer.phone:
                success, response = send_sms(customer.phone, sms_message)

                if success:
                    messages.success(request, "SMS notification sent successfully.")
                else:
                    messages.error(request, "SMS failed. Check logs.")
            else:
                messages.warning(request, "Customer has no phone number.")

            email_message = (
                f"Dear {customer.name},\n\n"
                f"Great news! Your laundry is ready for pickup.\n\n"
                f"Order Number : #{order.order_number}\n"
                f"Tracking ID: {order.tracking_id}\n"
                f"Total Amount: PHP {order.total_amount:.2f}\n"
                f"Amount Paid: PHP {order.amount_paid:.2f}\n"
                f"Balance Due: PHP {order.balance:.2f}\n\n"
                f"Please come and pick up your laundry at your earliest convenience.\n\n"
                f"Thank you for choosing FreshWave Laundry!\n"
                f"FreshWave Laundry Team"
            )
                #  EMAIL
            if customer.email:
                success = send_email(
                    customer.email,
                    f"Order Update #{order.order_number}",
                    email_message
                )
                if success:
                    messages.success(request, "Email sent successfully.")
                else:
                    messages.error(request, "Email failed to send.")

                return redirect("order_detail", order_number=order.order_number)

        if action == 'update_status':
            status_form = OrderStatusForm(request.POST, instance=order)
            if status_form.is_valid():
                order = update_order_status(order, status_form)
                messages.success(request, f'✅ Order status updated to "{order.get_status_display()}"')
                return redirect('order_detail', order_number=order.order_number)

        elif action == 'add_payment':
            payment_form = PaymentForm(request.POST)

        if not payment_form.is_valid():
            messages.error(request, "Cannot record payment. Please enter a valid amount.")
            return redirect('order_detail', order_number=order.order_number)

        try:
            payment = record_order_payment(order, payment_form)
            messages.success(request, f'✅ Payment of ₱{payment.amount} recorded!')
        except ValueError as error:
            messages.error(request, str(error))

        return redirect('order_detail', order_number=order.order_number)

    return render(request, 'laundry/orders/order_detail.html', {
        'order': order, 'status_form': status_form, 'payment_form': payment_form
    })


@login_required
def order_create(request):
    services = Service.objects.filter(is_active=True)
    customers = Customer.objects.all().order_by('name')

    customer_number = request.GET.get('customer')
    selected_customer = None

    if customer_number:
        selected_customer = get_object_or_404(
            Customer,
            customer_number=customer_number
        )
    
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        service_form = ServiceSelectionForm(request.POST)
        # Prevent validation issue when customer field is disabled
        if selected_customer:
            order_form.fields['customer'].required = False
        
        if order_form.is_valid():
            order = order_form.save(commit=False)

            # Auto-assign customer if opened from
            if selected_customer:
                order.customer = selected_customer
            else:
                order.customer = order_form.cleaned_data['customer']

            # Auto-assign order_number
            last_max = Order.objects.exclude(pk=order.pk if order.pk else 0).aggregate(
                m=Max('order_number'))['m'] or 0
            order.order_number = last_max + 1
            order.save()

            # Process services — quantity = weight_kg for per-kg pricing
            weight = float(order.weight_kg)
            for service in services:
                selected = request.POST.get(f'service_{service.id}')
                if selected:
                    OrderItem.objects.create(order=order, service=service, quantity=weight)

            # Email
            notify_order_received(order)
            
            # Create notification — order created
            Notification.objects.create(
                order=order,
                title=f'New Order #{order.order_number} Created',
                message=f'{order.customer.name} placed a new laundry order. Total: ₱{order.total_amount:.2f}',
                type='order',
            )

            messages.success(request, f'✅ Order #{order.order_number} created for {order.customer.name}!')
            return redirect('order_detail', order_number=order.order_number)
    else:
        initial_data = {}
        if selected_customer:
            initial_data['customer'] = selected_customer
        order_form = OrderForm(initial=initial_data)
        # Lock customer field if coming from customer detail
        if selected_customer:
            order_form.fields['customer'].disabled = True
        service_form = ServiceSelectionForm()
    
    return render(request, 'laundry/orders/order_form.html', {
        'order_form': order_form,
        'service_form': service_form,
        'services': services,
        'customers': customers,
        'selected_customer': selected_customer,
    })


@login_required
def order_delete(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'🗑️ Order #{order_number} deleted.')
        return redirect('order_list')
    return redirect('order_detail', order_number=order.order_number)


# ─── API ─────────────────────────────────────────────────────────────────────
@api_view(['GET'])
def api_customer_search(request):
    q = request.GET.get('q', '')
    customers = Customer.objects.filter(
        Q(name__icontains=q) | Q(phone__icontains=q)
    ).order_by('customer_number')[:10]
    data = [
        {
            'id':      c.id,
            'name':    c.name,
            'phone':   c.phone,
            'address': c.address,
            'initials': c.name[0].upper() if c.name else '?',
        }
        for c in customers
    ]
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)
