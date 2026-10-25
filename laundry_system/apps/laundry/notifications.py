from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import  render_to_string
import requests 

def send_sms(to_phone, message):
    try:
        # Convert PH number → E.164
        phone = to_phone.strip()
        if phone.startswith('0'):
            phone = '+63' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+63' + phone

        url = settings.UNISMS_BASE_URL

        payload = {
            "recipient": phone,
            "content": message,
        }
        response = requests.post(
            url,
            auth=(settings.UNISMS_API_KEY, ""), 
            json=payload,
            timeout=10
        )
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        print(f"✅ Message sent to {to_phone}")

        if response.status_code == 201:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False, str(e)


#  EMAIL via Django SMTP

def send_email(to_email, subject, message):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        print(f"✅ Email sent to {to_email}")
        return True, None
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False, str(e)


#  NOTIFICATION 

def notify_order_received(order):
    customer = order.customer
    services = ', '.join([item.service.get_name_display() for item in order.items.all()])

    email_message = (
        f"Dear {customer.name},\n\n"
        f"Your laundry order has been received!\n\n"
        f"Order Number: #{order.order_number} \n"
        f"Tracking ID: {order.tracking_id}\n" 
        f"Services: {services}\n"
        f"Total Amount: PHP {order.total_amount:.2f}\n\n"
        f"We will send you another notification when your laundry "
        f"is ready for pickup.\n\n"
        f"Thank you for choosing FreshWave Laundry!\n"
        f"FreshWave Laundry Services"
    )
    # Send Email (only if customer has email)
    if customer.email:
        send_email(
            customer.email,
            f"Order #{order.order_number} Received  FreshWave Laundry",
            email_message
        )


def notify_order_ready(order): 
    customer = order.customer

    sms_message = (
        f"{customer.name}, your laundry #{order.order_number} "
        f"is ready for pickup. Balance: PHP {order.balance:.2f}. "
        f"Thank you, FreshWave Laundry!"
    )
    email_message = (
        f"Dear {customer.name},\n\n"
        f"Great news! Your laundry is ready for pickup.\n\n"
        f"Order Number: #{order.order_number}\n"
        f"Tracking ID: {order.tracking_id} \n" 
        f"Total Amount: PHP {order.total_amount:.2f}\n"
        f"Amount Paid: PHP {order.amount_paid:.2f}\n"
        f"Balance Due: PHP {order.balance:.2f}\n\n"
        f"Please come and pick up your laundry at your earliest convenience.\n\n"
        f"Thank you for choosing FreshWave Laundry!\n"
        f"FreshWave Laundry Services"
    )

    send_sms(customer.phone, sms_message)

    if customer.email:
        send_email(
            customer.email,
            f"Your Laundry is Ready for Pickup!  Order #{order.order_number}",
            email_message
        )


def notify_order_completed(order):
    customer = order.customer
    email_message = (
        f"Dear {customer.name},\n\n"
        f"Your laundry Order #{order.order_number} w/ tracking ID - { order.tracking_id } has been completed.\n"
        f"Thank you for choosing FreshWave Laundry!\n\n"
        f"We hope to see you again soon.\n\n"
        f"FreshWave Laundry Services"
    )

    if customer.email:
        send_email(
            customer.email,
            f"Thank You! Order #{order.order_number} Completed - FreshWave Laundry",
            email_message
        )



def notify_payment_received(order, payment):
    customer = order.customer

    email_message = (
        f"Dear {customer.name},\n\n"
        f"We have received your payment.\n\n"
        f"Order Number: #{order.order_number}\n"
        f"Tracking ID: {order.tracking_id}\n" 
        f"Amount Paid: PHP {payment.amount:.2f}\n"
        f"Method: {payment.get_method_display()}\n"
        f"Reference: {payment.reference_no or 'N/A'}\n"
        f"Remaining Balance: PHP {order.balance:.2f}\n\n"
        f"Thank you for choosing us!\n"
        f"FreshWave Laundry Services"
    )

    if customer.email:
        send_email(
            customer.email,
            f"Payment Received - Order #{order.order_number}",
            email_message
        )