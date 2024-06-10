from django.apps import AppConfig


class GoogleLoginAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from .signals import handle_report_status_change 
        from django.db.models.signals import post_save
        from .models import Report
        post_save.connect(handle_report_status_change, sender=Report)