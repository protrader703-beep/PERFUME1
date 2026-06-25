"""
store/models.py

Core database models for the Attar e-commerce store:
  - Product       : The perfume/attar items sold
  - Order         : A customer's placed order with shipping + UPI payment info
  - OrderItem     : Individual line items within an order (product + qty)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Product(models.Model):
    """
    Represents a single Attar/Perfume product in the catalog.
    
    The 'slug' field is used in the URL so each product has a clean, 
    human-readable URL like /product/oud-al-arabian/ instead of /product/1/.
    
    'is_featured' marks products to be shown on the Home page hero/featured section.
    'is_active' lets the admin hide a product without deleting it (e.g., out of stock).
    """

    name = models.CharField(
        max_length=255,
        verbose_name="Product Name",
        help_text="Full name of the attar/perfume"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="URL Slug",
        help_text="Auto-generated URL-friendly name. Leave blank to auto-fill."
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Product Image",
        help_text="Main product photograph"
    )
    description = models.TextField(
        verbose_name="Full Description",
        help_text="Detailed description: scent notes, ingredients, longevity, etc."
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Short Description",
        help_text="One-line summary shown on product cards in the catalog"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Price (₹)",
        help_text="Selling price in Indian Rupees"
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock Quantity",
        help_text="Number of units currently available"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Featured on Homepage",
        help_text="If checked, this product will appear in the homepage featured section"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active / Visible",
        help_text="Uncheck to hide this product from the catalog without deleting it"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Added"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']  # Newest products shown first

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate the slug from the product name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def is_in_stock(self):
        """Helper to check if the product has stock available."""
        return self.stock > 0


class Order(models.Model):
    """
    Represents a customer's complete order.
    
    Stores:
    - Who placed it (linked to Django's User model)
    - Where to ship it (full shipping address fields)
    - Payment info (UPI transaction ID and optional screenshot)
    - Current order status (managed by the shop owner in admin)
    """

    # --- Order Status Choices ---
    STATUS_PENDING = 'pending'
    STATUS_PAYMENT_RECEIVED = 'payment_received'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending — Awaiting Payment Verification'),
        (STATUS_PAYMENT_RECEIVED, 'Payment Received'),
        (STATUS_PROCESSING, 'Processing — Being Prepared'),
        (STATUS_SHIPPED, 'Shipped — Out for Delivery'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    # --- Customer ---
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="Customer Account",
        help_text="The registered user who placed this order"
    )

    # --- Shipping Address ---
    full_name = models.CharField(
        max_length=255,
        verbose_name="Full Name",
        help_text="Recipient's full name for shipping"
    )
    email = models.EmailField(
        verbose_name="Email Address"
    )
    phone = models.CharField(
        max_length=15,
        verbose_name="Phone Number"
    )
    address_line1 = models.CharField(
        max_length=255,
        verbose_name="Address Line 1",
        help_text="House/Flat No., Street Name"
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Address Line 2",
        help_text="Area, Landmark (optional)"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="City"
    )
    state = models.CharField(
        max_length=100,
        verbose_name="State"
    )
    pincode = models.CharField(
        max_length=10,
        verbose_name="PIN Code"
    )

    # --- Order Financials ---
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Amount (₹)",
        help_text="Total amount customer should have paid via UPI"
    )

    # --- UPI Payment Info ---
    upi_transaction_id = models.CharField(
        max_length=100,
        verbose_name="UPI Transaction ID",
        help_text="Transaction reference number provided by the customer"
    )
    payment_screenshot = models.ImageField(
        upload_to='payment_screenshots/',
        null=True,
        blank=True,
        verbose_name="Payment Screenshot",
        help_text="Optional screenshot of UPI payment uploaded by customer"
    )

    # --- Order Management ---
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Order Status"
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name="Admin Notes",
        help_text="Internal notes (not visible to customer)"
    )

    # --- Timestamps ---
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Order Placed On"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']  # Newest orders at the top in admin

    def __str__(self):
        return f"Order #{self.id} — {self.full_name} — ₹{self.total_amount}"

    def get_status_display_class(self):
        """
        Returns a CSS class name based on order status.
        Used in templates to color-code the status badge.
        """
        status_classes = {
            self.STATUS_PENDING: 'status-pending',
            self.STATUS_PAYMENT_RECEIVED: 'status-payment',
            self.STATUS_PROCESSING: 'status-processing',
            self.STATUS_SHIPPED: 'status-shipped',
            self.STATUS_DELIVERED: 'status-delivered',
            self.STATUS_CANCELLED: 'status-cancelled',
        }
        return status_classes.get(self.status, 'status-pending')


class OrderItem(models.Model):
    """
    A single line item within an Order.
    
    We store 'price' at the time of ordering to preserve historical pricing.
    If you change a product's price later, existing orders won't be affected.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Order"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name="Product"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantity"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Unit Price at Purchase (₹)",
        help_text="Stored at time of order — not affected by future price changes"
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        return f"{self.quantity}x {product_name} (Order #{self.order.id})"

    def get_subtotal(self):
        """Calculate the line item total: quantity × unit price."""
        return self.quantity * self.price
