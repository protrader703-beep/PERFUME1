import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attar_store.settings")
django.setup()

from store.forms import CheckoutForm

data = {
    'full_name': 'Test User',
    'email': 'test@test.com',
    'phone': '1234567890',
    'address_line1': '123 Main St',
    'city': 'Test City',
    'state': 'Test State',
    'pincode': '123456'
}

form = CheckoutForm(data)
if not form.is_valid():
    print("Form is NOT valid!")
    print(form.errors)
else:
    print("Form is valid!")
    print(form.cleaned_data)
