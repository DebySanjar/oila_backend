from django.apps import AppConfig


class SosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sos'
    verbose_name = 'SOS System'
    
    def ready(self):
        import sos.signals  # noqa
