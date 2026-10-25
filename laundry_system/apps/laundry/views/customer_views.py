from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from apps.laundry.forms import CustomerForm
from apps.laundry.models import Customer

@login_required
def customer_list(request):
    q = request.GET.get('q', '').strip()
    customers = Customer.objects.all().order_by('customer_number')
    if q:
        customers = customers.filter(
            Q(name__icontains=q) | Q(phone__icontains=q) | Q(address__icontains=q)
        )
    all_customer_names = list(
        Customer.objects.order_by('name').values_list('name', flat=True)
    )

    return render(request, 'laundry/customers/customer_list.html', {
        'customers': customers,
        'query': q,
        'all_customer_names': all_customer_names,
    })

@login_required
def customer_detail(request, customer_number):
    customer = get_object_or_404(Customer, customer_number=customer_number)
    orders = customer.orders.all().order_by('-created_at')
    return render(request, 'laundry/customers/customer_detail.html', {'customer': customer, 'orders': orders})


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'✅ Customer "{customer.name}" added successfully!')
            return redirect('customer_detail', customer_number=customer.customer_number)
    else:
        form = CustomerForm()
    return render(request, 'laundry/customers/customer_form.html', {'form': form, 'title': 'Add New Customer'})


@login_required
def customer_edit(request, customer_number):
    customer = get_object_or_404(Customer, customer_number=customer_number)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            if not form.has_changed():
                messages.warning(request,'Customer information is already up to date.')
                return redirect('customer_edit',customer_number=customer_number)
            form.save()
            messages.success(request, f'✅ Customer "{customer.name}" updated successfully!')
            return redirect('customer_detail', customer_number=customer_number)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'laundry/customers/customer_form.html', {'form': form, 'title': 'Edit Customer', 'customer': customer})


@login_required
def customer_delete(request, customer_number):
    customer = get_object_or_404(Customer, customer_number=customer_number)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f'🗑️ Customer "{name}" deleted.')
        return redirect('customer_list')
    return redirect('customer_edit', customer_number=customer.customer_number)

