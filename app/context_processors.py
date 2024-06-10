from .models import Report
from django.db.models import Q

def status_change_count(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            status_change_count = Report.objects.filter(report_status_changed__gt=0).count()  
        else:
            notifs = Report.objects.filter(
                Q(reporter_email=request.user.email) & 
                Q(report_status_changed__gt=0))
            status_change_count = notifs.count()
            if request.path == '/notifications/':
                for n in notifs:
                    n.report_status_changed = 0
                    n.save()
    else:
        status_change_count = 0  
    
    return {'status_change_count': status_change_count}

