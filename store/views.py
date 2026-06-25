"""
store/views.py

All view functions for the store app.
A 'view' receives a web request and returns an HTML response.

Step 1 Note: These are placeholder views. In Step 3-5 we will fill 
in all the business logic. For now, they allow the server to run 
without errors so you can verify migrations and the admin panel work.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
from .forms import CheckoutForm, PaymentForm


# ============================================================
# HOME PAGE
# ============================================================

def home(request):
    """
    Home page — shows featured products.
    Products marked 'is_featured=True' in admin appear here.
    """
    featured_products = Product.objects.filter(is_featured=True, is_active=True)
    context = {
        'featured_products': featured_products,
        'page_title': 'Home — Attar Store',
    }
    return render(request, 'home.html', context)


# ============================================================
# SHOP / CATALOG
# ============================================================

def shop(request):
    """
    Shop page — lists all active products.
    In Step 3 we will add search and filtering.
    """
    products = Product.objects.filter(is_active=True)
    context = {
        'products': products,
        'page_title': 'Shop — All Attars',
    }
    return render(request, 'store/shop.html', context)


# ============================================================
# PRODUCT DETAIL
# ============================================================

def product_detail(request, slug):
    """
    Product detail page — shows full info for a single product.
    Uses the slug from the URL to look up the product.
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    context = {
        'product': product,
        'page_title': f'{product.name} — Attar Store',
    }
    return render(request, 'store/product_detail.html', context)


# ============================================================
# CART
# ============================================================

def cart(request):
    """
    Cart page — displays all items currently in the session cart.
    
    Cart data is stored in the session as:
    { 'product_id': quantity, ... }
    """
    cart_data = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id), is_active=True)
            subtotal = product.price * quantity
            cart_total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            # Product was deleted — remove from cart silently
            pass

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'page_title': 'Your Cart — Attar Store',
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request, product_id):
    """
    Adds a product to the session cart.
    If the product is already in the cart, increments the quantity.
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if not product.is_in_stock():
        messages.error(request, f'Sorry, {product.name} is currently out of stock.')
        return redirect('store:product_detail', slug=product.slug)

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1

    request.session['cart'] = cart
    request.session.modified = True  # Force Django to save the session

    messages.success(request, f'"{product.name}" has been added to your cart.')
    return redirect('store:cart')


def update_cart(request, product_id):
    """
    Updates the quantity of a specific product in the cart.
    Expects a POST request with 'quantity' field.
    """
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if quantity > 0:
            cart[product_id_str] = quantity
        else:
            # If quantity is 0, remove from cart
            cart.pop(product_id_str, None)

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('store:cart')


def remove_from_cart(request, product_id):
    """Removes a product completely from the session cart."""
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, 'Item removed from cart.')
    return redirect('store:cart')


# ============================================================
# CHECKOUT
# ============================================================

@login_required
def checkout(request):
    cart_data = request.session.get('cart', {})
    if not cart_data:
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('store:shop')
        
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Save the clean data in the session for the payment step
            request.session['shipping_info'] = form.cleaned_data
            return redirect('store:payment')
    else:
        # Pre-fill with user's profile data
        from accounts.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': profile.phone,
            'address_line1': profile.address_line1,
            'city': profile.city,
            'state': profile.state,
            'pincode': profile.pincode,
        }
        form = CheckoutForm(initial=initial_data)

    # Build cart items for the order summary sidebar
    cart_items = []
    cart_total = 0
    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id), is_active=True)
            subtotal = product.price * quantity
            cart_total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'page_title': 'Checkout — Attar Store',
    }
    return render(request, 'store/checkout.html', context)

# ============================================================
# PAYMENT (UPI QR CODE PAGE)
# ============================================================

@login_required
def payment(request):
    cart_data = request.session.get('cart', {})
    shipping_info = request.session.get('shipping_info')
    
    if not cart_data or not shipping_info:
        messages.error(request, 'Please complete the shipping step first.')
        return redirect('store:checkout')
        
    # Calculate Total
    total_amount = 0
    for product_id, qty in cart_data.items():
        try:
            p = Product.objects.get(id=int(product_id), is_active=True)
            total_amount += p.price * qty
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # 1. Create the Order
            order = Order.objects.create(
                customer=request.user,
                full_name=shipping_info['full_name'],
                email=shipping_info['email'],
                phone=shipping_info['phone'],
                address_line1=shipping_info['address_line1'],
                city=shipping_info['city'],
                state=shipping_info['state'],
                pincode=shipping_info['pincode'],
                total_amount=total_amount,
                upi_transaction_id=form.cleaned_data['upi_transaction_id']
            )
            
            # 2. Create OrderItems and adjust stock
            for product_id, qty in cart_data.items():
                try:
                    product = Product.objects.get(id=int(product_id), is_active=True)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=product.price
                    )
                    # Reduce stock
                    if product.stock >= qty:
                        product.stock -= qty
                    else:
                        product.stock = 0 # Fallback
                    product.save()
                except Product.DoesNotExist:
                    pass
            
            # 3. Clear session
            request.session.pop('cart', None)
            request.session.pop('shipping_info', None)
            request.session.modified = True
            
            # 4. Redirect to success
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('store:order_success', order_id=order.id)
    else:
        form = PaymentForm()

    context = {
        'form': form,
        'total_amount': total_amount,
        'page_title': 'Complete Payment — Attar Store',
    }
    return render(request, 'store/payment.html', context)


# ============================================================
# ORDER SUCCESS
# ============================================================

@login_required
def order_success(request, order_id):
    """
    Thank-you page shown after a successful order placement.
    Only accessible if the order belongs to the logged-in user.
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    context = {
        'order': order,
        'page_title': 'Order Placed Successfully!',
    }
    return render(request, 'store/order_success.html', context)


# ============================================================
# STATIC / TRUST PAGES
# ============================================================

def about(request):
    return render(request, 'pages/about.html', {'page_title': 'About Us'})


def contact(request):
    return render(request, 'pages/contact.html', {'page_title': 'Contact Us'})


def return_policy(request):
    return render(request, 'pages/return_policy.html', {'page_title': 'Return Policy'})
