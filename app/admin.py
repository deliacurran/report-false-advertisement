from django.contrib import admin
from .models import Report, ReportS3File

def mark_review_in_progress(modeladmin, request, queryset):
    queryset.update(status='Review-In-Progress')
mark_review_in_progress.short_description = "Update status of reports to Review-In-Progress"

def mark_review_completed(modeladmin, request, queryset):
    queryset.update(status='Review-Completed')
mark_review_completed.short_description = "Update status of reports to Review-Completed"

class ReportS3FileInline(admin.TabularInline):
    model = ReportS3File
    extra = 0


class ReportAdmin(admin.ModelAdmin):
    inlines = [
        ReportS3FileInline,
    ]
    list_display = ['id', 'status']
    actions = [mark_review_in_progress, mark_review_completed]


admin.site.register(Report, ReportAdmin)
