"""
accounts/apps.py

App config for accounts — also connects the signals so they are 
loaded when the app starts up.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Customer Accounts'

    def ready(self):
        """
        This method runs when the app is loaded.
        Importing signals here ensures they are registered at startup.
        """
        import accounts.signals  # noqa: F401
