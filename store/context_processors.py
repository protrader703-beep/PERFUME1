"""
store/context_processors.py

Template context processors run on every request and inject variables
into every template automatically.

'cart_count' injects the number of items in the user's cart into all 
templates so the navbar cart icon can always show the current count.
"""


def cart_count(request):
    """
    Reads the cart from the session and returns the total item count.
    
    The cart is stored in session as:
    {
        'product_id_as_string': quantity,
        ...
    }
    """
    cart = request.session.get('cart', {})
    count = sum(cart.values())  # Sum all quantities
    return {'cart_count': count}
