"""
store/urls.py

URL routing for the store app.
All product, cart, checkout, and static page URLs are defined here.
"""

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # --- Home ---
    path('', views.home, name='home'),

    # --- Shop / Catalog ---
    path('shop/', views.shop, name='shop'),

    # --- Product Detail (uses slug for clean URL) ---
    # Example: /product/oud-al-arabian/
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # --- Cart ---
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # --- Checkout ---
    path('checkout/', views.checkout, name='checkout'),

    # --- Payment (UPI QR Code page) ---
    path('payment/', views.payment, name='payment'),

    # --- Order Success ---
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # --- Static / Trust Pages ---
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('return-policy/', views.return_policy, name='return_policy'),
]
