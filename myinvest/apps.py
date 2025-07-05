from django.apps import AppConfig


class MyinvestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myinvest"
    verbose_name = "Sistema de Investimento Imobiliário"

    def ready(self):
        import myinvest.signals  # noqa
