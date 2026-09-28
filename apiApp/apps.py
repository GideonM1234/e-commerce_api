from django.apps import AppConfig


class ApiappConfig(AppConfig):
    name = 'apiApp'

    def ready(self):
        import apiApp.signals 