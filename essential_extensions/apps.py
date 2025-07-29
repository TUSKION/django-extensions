from django.apps import AppConfig


class EssentialExtensionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'essential_extensions'
    verbose_name = 'Essential Extensions'

    def ready(self):
        """Import signals when the app is ready."""
        import essential_extensions.signals 