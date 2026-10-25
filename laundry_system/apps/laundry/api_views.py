from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum, Q
from datetime import date
from .models import Customer, Order, Payment, Service
from .serializers import (
    CustomerSerializer, OrderSerializer,
    PaymentSerializer, ServiceSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = CustomerSerializer
    queryset           = Customer.objects.select_related('customer').order_by('customer_number')

    def get_queryset(self):
        q = self.request.query_params.get('q', '')
        qs = Customer.objects.all().select_related('customer').order_by('customer_number')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(phone__icontains=q) |
                Q(address__icontains=q)
            )
        return qs


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = OrderSerializer
    queryset           = Order.objects.select_related('customer').order_by('created_at')

    def get_queryset(self):
        qs     = Order.objects.select_related('customer').order_by('created_at')
        status = self.request.query_params.get('status', '')
        q      = self.request.query_params.get('q', '')
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(Q(customer__name__icontains=q) | Q(id__icontains=q))
        return qs

    # GET /api/orders/<id>/payments/
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        order    = self.get_object()
        payments = order.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = PaymentSerializer
    queryset           = Payment.objects.select_related('order__customer').order_by('-paid_at')

    def get_queryset(self):
        qs          = Payment.objects.select_related('order__customer').order_by('-paid_at')
        date_filter = self.request.query_params.get('date', '')
        if date_filter:
            from datetime import datetime
            try:
                d  = datetime.strptime(date_filter, '%Y-%m-%d').date()
                qs = qs.filter(paid_at__date=d)
            except ValueError:
                pass
        return qs


class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = ServiceSerializer
    queryset           = Service.objects.all().order_by('name')


# ── Summary / Stats endpoint ──────────────────────────────────
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        data = {
            'total_customers':  Customer.objects.count(),
            'active_orders':    Order.objects.exclude(status__in=['completed','cancelled']).count(),
            'completed_orders': Order.objects.filter(status='completed').count(),
            'today_revenue':    Payment.objects.filter(
                                    paid_at__date=today, status='paid'
                                ).aggregate(t=Sum('amount'))['t'] or 0,
        }
        return Response(data)