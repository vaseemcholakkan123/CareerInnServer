from django.apps import AppConfig


class EmployerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Employer'
    def ready(self):
        import Employer.signals