from django.apps import AppConfig


class IcfinderAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "icfinder_app"

    def ready(self):
        import icfinder_app.signals