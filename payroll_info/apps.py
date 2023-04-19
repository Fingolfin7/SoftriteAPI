from django.apps import AppConfig


class PayrollInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payroll_info'

    def ready(self):
        import payroll_info.signals
