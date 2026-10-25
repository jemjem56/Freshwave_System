from rest_framework import serializers
from .models import Customer, Order, OrderItem, Payment, Service


class ServiceSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    class Meta:
        model = Service
        fields = ['name', 'name_display', 'price', 'description', 'is_active']


class CustomerSerializer(serializers.ModelSerializer):
    total_orders  = serializers.IntegerField(read_only=True)
    active_orders = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['customer_number', 'name', 'phone', 'address', 'email',
                'total_orders', 'active_orders', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.get_name_display', read_only=True)
    subtotal     = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = OrderItem
        fields = ['service_name', 'quantity', 'subtotal']


class PaymentSerializer(serializers.ModelSerializer):
    paid_at = serializers.DateTimeField(required=False, allow_null=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'method', 'method_display',
                'status', 'status_display', 'reference_no', 'notes', 'paid_at']


class OrderSerializer(serializers.ModelSerializer):
    pickup_date = serializers.DateTimeField(required=False, allow_null=True)
    customer_name  = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items          = OrderItemSerializer(many=True, read_only=True)
    payments       = PaymentSerializer(many=True, read_only=True)
    total_amount   = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid    = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance        = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_paid        = serializers.BooleanField(read_only=True)
    class Meta:
        model = Order
        fields = ['order_number', 'customer_name', 'customer_phone',
                'status_display', 'weight_kg', 'notes',
                'pickup_date', 'items', 'payments',
                'total_amount', 'amount_paid', 'balance', 'is_paid',
                'created_at', 'updated_at']