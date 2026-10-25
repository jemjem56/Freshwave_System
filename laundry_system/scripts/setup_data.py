import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.laundry.models import Service, Customer, Order, OrderItem, Payment
from decimal import Decimal

print(" FreshWave Laundry - Setup")
print("=" * 40)

# Create superuser
if not User.objects.filter(username='Freshwave').exists():
    User.objects.create_superuser('Freshwave', 'freshwavelaundry7@gmail.com', 'freshwave7')
    print("✅ Admin user created: Freshwave / freshwave7")
else:
    print("ℹ️  Admin user already exists")

# Reset and recreate services cleanly
Service.objects.all().delete()
services_data = [
    {'name': 'washing',      'price': Decimal('25.00'),  'description': 'Full wash cycle with detergent'},
    {'name': 'drying',       'price': Decimal('20.00'),  'description': 'Machine drying service'},
    {'name': 'folding',      'price': Decimal('5.00'),  'description': 'Professional folding'},
    {'name': 'ironing',      'price': Decimal('40.00'),  'description': 'Steam ironing per kg'},
    {'name': 'bleaching',    'price': Decimal('20.00'),  'description': 'Whitening Treatment & Remove Stains'},
    {'name': 'package',      'price': Decimal('220.00'),  'description': 'Complete laundry package'},
]

for s in services_data:
    obj = Service.objects.create(
        name=s['name'],
        price=s['price'],
        description=s['description']
    )
    print(f"✅ Service created: {obj.get_name_display()} @ ₱{obj.price}/kg")

# Create sample customers
sample_customers = [
    {'name': 'James Panugaling', 'phone': '09096812170', 'address': 'Brgy. Babag, Cebu City','email': 'jamespanugaling16@email.com'},
    {'name': 'Jem Bonghanoy', 'phone': '09850115870', 'address': 'Brgy. Babag, Cebu City','email': 'jembonghanoy.dev.ph@email.com'},
    {'name': 'Ailyn Decasa', 'phone': '09670094423', 'address': 'Brgy. Sapangdaku, Cebu City','email': 'decasaailyn04@gmail.com'},
]

for c in sample_customers:
    obj, created = Customer.objects.get_or_create(
        phone=c['phone'],
        defaults={'name': c['name'], 'address': c['address'], 'email': c['email'] or None}
    )
    if created:
        print(f"✅ Customer created: {obj.name}")
    else:
        print(f"ℹ️  Customer exists: {obj.name}")

# Create sample orders
if Customer.objects.exists() and Service.objects.exists():
    washing = Service.objects.get(name='washing')
    drying  = Service.objects.get(name='drying')
    folding = Service.objects.get(name='folding')
    ironing = Service.objects.get(name='ironing')
    bleaching = Service.objects.get(name='bleaching')
    package = Service.objects.get(name='package')

    customers = list(Customer.objects.all())

    orders_data = [
        {'customer': customers[0], 'status': 'received', 'weight': 2.5, 'services': [washing, drying, folding]},
        {'customer': customers[1], 'status': 'drying', 'weight': 3.2, 'services': [washing, drying, ironing]},
        {'customer': customers[2], 'status': 'ready', 'weight': 5.0, 'services': [washing, folding, bleaching, drying]},    ]

    for od in orders_data:
        if not Order.objects.filter(customer=od['customer'], status=od['status']).exists():
            order = Order.objects.create(
                customer=od['customer'],
                status=od['status'],
                weight_kg=od['weight'],
                notes='No notes'
            )
            for svc in od['services']:
                OrderItem.objects.create(order=order, service=svc, quantity=od['weight'])

            if od['status'] == 'completed':
                Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    method='cash',
                    status='paid'
                )
            print(f"✅ Order created: #{order.order_number} for {od['customer'].name} [{od['status']}]")

print("=" * 40)
print("Login at: http://127.0.0.1:8000/")
print("Admin at: http://127.0.0.1:8000/admin/")
print("  Username: Freshwave")
print("  Password: freshwave7")