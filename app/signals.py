from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Report, Notification
from django.db.models import F
from django.utils import timezone


class App(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    def ready(self):
        import app.signals

# create notifications when report status changes
@receiver(post_save, sender=Report)
def handle_report_status_change(sender, instance, **kwargs):
    if kwargs.get('update_fields') is not None and 'status' in kwargs['update_fields']:
        old_status = instance.status
        new_status = instance.get_status_display()
        if old_status != new_status:
            Notification.objects.create(
                user = instance.user,  
                report = instance,
                message = f"report #{instance.id}: status changed from {old_status} to {new_status}",
                timestamp = timezone.now()
            )
            Report.objects.filter(id=instance.id).update(report_status_changed=F('report_status_changed') + 1)

