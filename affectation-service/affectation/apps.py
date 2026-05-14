from django.apps import AppConfig


class AffectationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'affectation'

    def ready(self):

        from affectation.eureka_client import start_eureka_client
        start_eureka_client()


