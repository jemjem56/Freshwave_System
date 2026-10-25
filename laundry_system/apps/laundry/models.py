import uuid
from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone


class Customer(models.Model):
    customer_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['customer_number']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.customer_number:
                last_customer = (
                    Customer.objects
                    .select_for_update()
                    .order_by('-customer_number')
                    .first()
                )
                self.customer_number = (
                    last_customer.customer_number + 1 
                    if last_customer and last_customer.customer_number 
                    else 1
                )
            super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.phone})"

    @property
    def total_orders(self):
        return self.orders.count()

    @property
    def active_orders(self):
        return self.orders.exclude(status__in=['completed', 'cancelled']).count()


class Service(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('promo', 'Promo Package'),
    ]
    name = models.CharField(max_length=100, unique=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='regular')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']

    @property
    def is_package(self):
        return self.service_type == 'promo'   

    def get_name_display(self):
        return self.name.title()

    def __str__(self):
        return f"{self.get_name_display()} - ₱{self.price}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('washing', 'Washing'),
        ('drying', 'Drying'),
        ('folding', 'Folding'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    order_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    services = models.ManyToManyField(Service, through='OrderItem')
    tracking_id = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, default=1.0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Order number
            if not self.order_number:
                last_order = (
                    Order.objects
                    .select_for_update()
                    .order_by('-order_number')
                    .first()
                )
                self.order_number = (
                    last_order.order_number + 1
                    if last_order and last_order.order_number
                    else 1
                )
            #  Tracking ID  
            if not self.tracking_id:
                self.tracking_id = f"FW-{uuid.uuid4().hex[:8].upper()}"

            super().save(*args, **kwargs)

    def __str__(self):
        num = self.order_number if self.order_number else self.id
        return f"Order #{num} - {self.customer.name}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def is_paid(self):
        return self.amount_paid >= self.total_amount

    @property
    def amount_paid(self):
        payments = self.payments.exclude(status='refunded')
        total = sum((p.amount for p in payments), Decimal('0.00'))
        return total

    @property
    def balance(self):
        remaining = self.total_amount - self.amount_paid
        return remaining if remaining > Decimal('0.00') else Decimal('0.00')

    @property
    def status_badge_color(self):
        colors = {
            'received': 'info',
            'washing': 'primary',
            'drying': 'warning',
            'folding': 'secondary',
            'ready': 'success',
            'completed': 'dark',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')
    
class SMSLog(models.Model):
    phone = models.CharField(max_length=20)
    message = models.TextField()
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="pending")
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1.0)
    
    class Meta:
        ordering = ['id']

    @property
    def subtotal(self):
        return self.service.price * self.quantity

    def __str__(self):
        return f"{self.service.get_name_display()} x {self.quantity}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
    ]

    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('gcash', 'GCash'),
        ('maya', 'Maya'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_no = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        num = self.order.order_number if self.order.order_number else self.order.id
        return f"Payment ₱{self.amount} for Order #{num}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('order',   'Order Created'),
        ('payment', 'Payment Recorded'),
        ('status',  'Status Updated'),
        ('ready',   'Ready for Pickup'),
        ('info',    'Information'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
