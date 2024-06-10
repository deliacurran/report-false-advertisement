from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone


class Report(models.Model):
    CATEGORY_CHOICES = [
        ('Food','Food'),
        ('Retail','Retail'),
        ('Jobs','Jobs'),
        ('Services','Services'),
        ('Medical','Medical'),
        ('Other','Other'),
    ]
    STATUS_CHOICES = [
        ('Review-Pending', 'Review-Pending'),
        ('Review-In-Progress', 'Review-In-Progress'),
        ('Review-Completed', 'Review-Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    report_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reporter_email = models.CharField(max_length=200, default='Anonymous')
    reason = models.TextField(max_length=300)
    company_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Review-Pending')
    report_status_changed = models.IntegerField(default=0)
    report_date = models.DateTimeField(default=timezone.now)
    admin_notes = models.TextField(default="No notes provided.")

    def __str__(self):
        return self.reason + " reported by " + (self.user.email if self.user else 'Anonymous')

    def likes_count(self):
        return self.likes.count()

class ReportLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, related_name='likes', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'report')

    def __str__(self):
        return f"{self.user.username} liked {self.report}"


class ReportS3File(models.Model):
    report = models.ForeignKey(Report,
                               related_name='s3_files',
                               on_delete=models.CASCADE)
    s3_key = models.CharField(max_length=1024)

    def __str__(self):
        return f"S3 Key: {self.s3_key} for Report: {self.report.report_uuid}"
    

class Notification(models.Model):
    MESSAGE_CHOICES = [
        ('Report-Submitted-For-Review', 'Report-Submitted-For-Review'),
        ('Report-Review-Started', 'Report-Review-Started'),
        ('Report-Review-Completed', 'Report-Review-Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    message = models.TextField( choices=MESSAGE_CHOICES, default='Report-Submitted-For-Review')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message + "for report: " + self.report

