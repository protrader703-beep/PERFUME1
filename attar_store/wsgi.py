"""
WSGI config for attar_store project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attar_store.settings')

application = get_wsgi_application()
