from django.apps import AppConfig


class PropertyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'property_app'

    def ready(self):
        # Preload the sentence transformer model when Django starts
        # This avoids slow first request
        try:
            from .services import get_model
            get_model()
            print('Sentence transformer model preloaded successfully.')
        except Exception as e:
            print(f'Model preload failed: {e}')