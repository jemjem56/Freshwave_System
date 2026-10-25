from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import api_views, views

router = DefaultRouter()
router.register(r'customers', api_views.CustomerViewSet, basename='api-customers')
router.register(r'orders',    api_views.OrderViewSet,    basename='api-orders')
router.register(r'payments',  api_views.PaymentViewSet,  basename='api-payments')
router.register(r'services',  api_views.ServiceViewSet,  basename='api-services')

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:customer_number>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_number>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:customer_number>/delete/', views.customer_delete, name='customer_delete'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:order_number>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_number>/delete/', views.order_delete, name='order_delete'),

    # Payments
    path('payments/', views.payment_list, name='payment_list'),

    # Services
    path('services/', views.service_list, name='service_list'),

    # Notifications
    path('notifications/<int:pk>/read/',   views.mark_notification_read,   name='mark_read'),
    path('notifications/mark-all-read/',   views.mark_all_read,            name='mark_all_read'),
    path('notifications/<int:pk>/delete/', views.delete_notification,      name='delete_notification'),
    path('notifications/delete-all/',      views.delete_all_notifications, name='delete_all_notifications'),

    # API customer search
    path('api/customers/', views.api_customer_search, name='api_customer_search'),

    # DRF API
    path('api/', include(router.urls)),
    path('api/dashboard/', api_views.DashboardStatsView.as_view(), name='api-dashboard'),
    path('api/auth/', include('rest_framework.urls')),
]



