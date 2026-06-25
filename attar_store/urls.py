"""
URL configuration for attar_store project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Store app (home, products, cart, checkout, orders)
    path('', include('store.urls')),

    # Accounts app (login, signup, profile, password reset)
    path('accounts/', include('accounts.urls')),

    # Django's built-in password reset URLs
    path('accounts/', include('django.contrib.auth.urls')),
]

# Serve media files during development (product images, payment screenshots)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
