from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address_line1', 'city', 'state', 'pincode']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['upi_transaction_id']
        labels = {
            'upi_transaction_id': 'UPI Transaction ID'
        }
