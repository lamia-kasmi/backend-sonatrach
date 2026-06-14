from django.apps import AppConfig


class ClmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clm'
    def ready(self):

        from clm.eureka_client import start_eureka_client
        start_eureka_client()

