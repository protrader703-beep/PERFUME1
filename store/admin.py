"""
store/admin.py

Registers all store models with Django's built-in admin panel.
The admin panel (accessible at /admin/) gives the shop owner full control to:
  - Add, edit, delete products
  - View and manage incoming orders
  - Update order status (Pending → Shipped → Delivered)
  - Verify UPI payment screenshots and transaction IDs
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, OrderItem


# ============================================================
# PRODUCT ADMIN
# ============================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Product model.
    Shows a rich listing with image preview and quick-toggle controls.
    """

    # Columns visible in the product list view
    list_display = [
        'product_image_preview',
        'name',
        'price',
        'stock',
        'is_featured',
        'is_active',
        'created_at',
    ]

    # Fields that can be clicked to open the edit page
    list_display_links = ['product_image_preview', 'name']

    # Fields that can be edited directly in the list view (without opening)
    list_editable = ['price', 'stock', 'is_featured', 'is_active']

    # Sidebar filters
    list_filter = ['is_featured', 'is_active', 'created_at']

    # Search bar — searches these fields
    search_fields = ['name', 'description', 'short_description']

    # Auto-populate slug from name
    prepopulated_fields = {'slug': ('name',)}

    # Number of products per page in list view
    list_per_page = 20

    # Field grouping on the edit/add page
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'short_description', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock')
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_active')
        }),
    )

    def product_image_preview(self, obj):
        """Show a small thumbnail in the admin list."""
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px; width:50px; object-fit:cover; border-radius:4px;" />',
                obj.image.url
            )
        return "No Image"
    product_image_preview.short_description = "Image"


# ============================================================
# ORDER ITEM INLINE (shown inside Order detail page)
# ============================================================

class OrderItemInline(admin.TabularInline):
    """
    Displays all items of an order directly on the Order detail page.
    This is read-only so the owner can see what was ordered without 
    accidentally editing the historical purchase data.
    """
    model = OrderItem
    extra = 0  # Don't show empty extra rows
    readonly_fields = ['product', 'quantity', 'price', 'get_subtotal']
    can_delete = False

    def get_subtotal(self, obj):
        return f"₹{obj.get_subtotal()}"
    get_subtotal.short_description = "Subtotal"


# ============================================================
# ORDER ADMIN
# ============================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Order model.
    Gives the shop owner a full dashboard to manage all incoming orders.
    """

    # Columns in the order list view
    list_display = [
        'id',
        'full_name',
        'phone',
        'total_amount',
        'upi_transaction_id',
        'colored_status',
        'created_at',
    ]

    list_display_links = ['id', 'full_name']

    # The owner can change the order status directly from the list view
    list_editable = ['colored_status'] if False else []  # Inline edit disabled for safety

    # Filters in the right sidebar
    list_filter = ['status', 'created_at', 'state']

    # Search: search by name, phone, email, or UPI ID
    search_fields = ['full_name', 'phone', 'email', 'upi_transaction_id', 'id']

    # Show order items inline inside the order detail page
    inlines = [OrderItemInline]

    # Read-only fields that should not be edited by admin
    readonly_fields = ['created_at', 'updated_at', 'customer', 'total_amount']

    # Orders per page
    list_per_page = 25

    # Action: Bulk mark as shipped
    actions = ['mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    # Field layout on the Order detail/edit page
    fieldsets = (
        ('Order Status', {
            'fields': ('status', 'admin_notes'),
            'description': 'Update the order status and add internal notes here.'
        }),
        ('Customer & Payment Info', {
            'fields': ('customer', 'total_amount', 'upi_transaction_id', 'payment_screenshot')
        }),
        ('Shipping Address', {
            'fields': (
                'full_name', 'email', 'phone',
                'address_line1', 'address_line2',
                'city', 'state', 'pincode'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsed by default
        }),
    )

    def colored_status(self, obj):
        """Display the order status with a color-coded badge in the admin list."""
        colors = {
            'pending': '#FFA500',           # Orange
            'payment_received': '#1E90FF',  # Blue
            'processing': '#9932CC',        # Purple
            'shipped': '#32CD32',           # Green
            'delivered': '#008000',         # Dark Green
            'cancelled': '#DC143C',         # Red
        }
        color = colors.get(obj.status, '#888888')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    colored_status.short_description = "Status"

    # --- Bulk Action Methods ---

    def mark_as_shipped(self, request, queryset):
        """Bulk action: Mark selected orders as Shipped."""
        updated = queryset.update(status=Order.STATUS_SHIPPED)
        self.message_user(request, f"{updated} order(s) marked as Shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        """Bulk action: Mark selected orders as Delivered."""
        updated = queryset.update(status=Order.STATUS_DELIVERED)
        self.message_user(request, f"{updated} order(s) marked as Delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        """Bulk action: Mark selected orders as Cancelled."""
        updated = queryset.update(status=Order.STATUS_CANCELLED)
        self.message_user(request, f"{updated} order(s) marked as Cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"


# ============================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================

admin.site.site_header = "Attar Store — Admin Panel"
admin.site.site_title = "Attar Store Admin"
admin.site.index_title = "Welcome, Shop Owner! Manage Your Store Here."
