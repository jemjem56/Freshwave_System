from django import forms
from decimal import Decimal
from .models import Customer, Order, Payment, Service


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan Dela Cruz'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 09xxxxxxxxx'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '123 St, Cebu City'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'weight_kg', 'notes', 'pickup_date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.1', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special instructions...'}),
            'pickup_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'reference_no', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference number (optional)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise forms.ValidationError("Amount is required.")
        if amount <= Decimal("0.00"):
            raise forms.ValidationError("Payment amount must be greater than 0.00.")

        return amount


class ServiceSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        services = Service.objects.filter(is_active=True)
        for service in services:
            self.fields[f'service_{service.id}'] = forms.BooleanField(
                required=False,
                label=f"{service.get_name_display()} (₱{service.price}/kg)",
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-price': str(service.price), 'data-id': service.id})
            )
            self.fields[f'qty_{service.id}'] = forms.DecimalField(
                required=False,
                initial=1.0,
                min_value=1.0,
                label='Qty/kg',
                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm qty-input', 'min': '1.0', 'step': '0.1', 'value': '1', 'data-id': service.id})
            )
