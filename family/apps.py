from django.apps import AppConfig


class FamilyConfig(AppConfig):
    """Family app configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'family'
    verbose_name = 'Oilaviy Funksiyalar'
    
    def ready(self):
        """Import signals when app is ready"""
        import family.signals
    verbose_name = 'Family Tasks & Chat'
    
    def ready(self):
        import family.signals  # noqa
