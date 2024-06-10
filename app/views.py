from django.contrib.auth import logout
from django.contrib.auth import login as dj_login
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import ReportForm, customLogin, customSignUp, CompleteForm
from .s3 import upload, generate_presigned_url, delete_file
import uuid
from django.contrib import messages
from .models import ReportS3File, Notification
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from .models import ReportLike
from django.shortcuts import render
from .models import Report
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend


import logging


def signUp(request):
    if request.method == 'POST':
        form = customSignUp(request.POST)
        if form.is_valid():
            user = form.save(request)
            backend = ModelBackend()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            dj_login(request, user)
            return redirect('/')
    else:
        form = customSignUp()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = customLogin(data=request.POST, request=request)
        if form.is_valid():
            remember_me = form.cleaned_data.get('remember_me')
            if not remember_me:
                request.session.set_expiry(0)
            form.login(request)
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')

    else:
        form = customLogin()

    context = {
        'login_form': form,
    }
    return render(request, 'login.html', context)


def logOut(request):
    logout(request)
    return redirect('/')


def index(request):
    reports = Report.objects.all()
    query = request.GET.get('q')
    company_query = request.GET.get('company_name')
    category_query = request.GET.get('category')


    if company_query:
        reports = reports.filter(company_name__icontains=company_query)
    if category_query:
        reports = reports.filter(category__icontains=category_query)


    sort_by_likes = request.GET.get('sort_by_likes', 'false') == 'true'

    if sort_by_likes:
        reports = reports.annotate(likes_count=Count('likes')).order_by('-likes_count')
    else:
        reports = reports.order_by('-report_date')

    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        report = Report.objects.get(id=report_id)

        if request.user.is_authenticated:
            if ReportLike.objects.filter(user=request.user,
                                         report=report).exists():
                ReportLike.objects.filter(user=request.user,
                                          report=report).delete()
            else:
                ReportLike.objects.create(user=request.user, report=report)
        else:
            return redirect('app:login')
    if request.user.is_authenticated:
        for report in reports:
            report.user_liked = ReportLike.objects.filter(
                user=request.user, report=report).exists()


    for report in reports:
        report.share_url = request.build_absolute_uri(
            reverse("app:index")) + f"#report-{report.id}"
        #print(report.share_url)

    toggle_sort_parameter = 'false' if sort_by_likes else 'true'
    toggle_sort_url = f"?sort_by_likes={toggle_sort_parameter}"
    context = {
        'reports': reports,
        'query': query,
        'sort_by_likes': sort_by_likes,
        'toggle_sort_url': toggle_sort_url,

    }

    return render(request, 'index.html', context)


def report_success(request):
    return render(request, 'report_success.html')


def generate_uuid():
    return uuid.uuid4()


def report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report_instance = form.save(commit=False)
            if request.user.is_authenticated:
                report_instance.user = request.user
                report_instance.reporter_email = request.user.email
            report_instance.save()

            upload_success = True
            for file in request.FILES.getlist("files"):
                file_name = str(file)
                file_name = f"{generate_uuid().hex[:8]}_{file_name}"
                key = f"uploads/{report_instance.report_uuid}/{file_name}"
                if upload(file, key):
                    print(f"Upload success: {key}")
                    ReportS3File.objects.create(report=report_instance,
                                                s3_key=key)
                else:
                    print(f"Upload failed for {key}")
                    upload_success = False
                    break

            if not upload_success:
                print("Upload of one or more files failed. Report not saved.")
                report_instance.delete()
            else:
                return HttpResponseRedirect(reverse("app:report_success"))
    else:
        form = ReportForm()

    return render(request, "reportform.html", {'form': form})


def report_list(request):
    if request.user.is_authenticated:
        if request.user.is_superuser and not request.user.is_staff:
            reports = Report.objects.all().order_by('-report_date')
        else:
            reports = Report.objects.filter(reporter_email=request.user.email).order_by('-report_date')
    elif not request.user.is_authenticated:
        messages.info(request, 'You need to be logged in to view your reports. Please use the tabs on the navigation bar to access different pages!')
        return redirect('app:login')

    return render(request, 'report_list.html', {'reports': reports})


def report_detail(request, report_uuid):
    report = get_object_or_404(Report, report_uuid=report_uuid)

    if request.user.is_superuser and not request.user.is_staff and report.status == 'Review-Pending':
        mark_review_in_progress(request, report)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'like' in request.POST:
                ReportLike.objects.get_or_create(user=request.user,
                                                 report=report)
            elif 'unlike' in request.POST:
                ReportLike.objects.filter(user=request.user,
                                          report=report).delete()
            return redirect('app:report_detail', report_uuid=report_uuid)
        else:
            return redirect('login')

    s3_files = report.s3_files.all()
    presigned_urls = []
    for file in s3_files:
        presigned_url = generate_presigned_url(file.s3_key)
        file_name = file.s3_key.split('/')[-1]
        file_type = file_name.split('.')[-1]
        presigned_urls.append((file_name, presigned_url, file_type))

    reporter_email = 'Anonymous'
    reporter_name = 'Anonymous'
    if report.user:
        reporter_email = report.user.email
        reporter_name = report.user.username

    context = {
        'report':
        report,
        'presigned_urls':
        presigned_urls,
        'reporter_email':
        reporter_email,
        'reporter_name':
        reporter_name,
        'user_liked':
        ReportLike.objects.filter(user=request.user, report=report).exists(),
    }

    return render(request, 'report_detail.html', context)

@login_required
def delete_report(request, report_uuid):
    report = get_object_or_404(Report, report_uuid=report_uuid)
    # get all s3 files associated with the report
    s3_files = report.s3_files.all()
    for file in s3_files:
        # delete the s3 file
        delete_file(file.s3_key)
        print(f"Deleted file: {file.s3_key}")

    if request.user == report.user:
        report.delete()
    return redirect('app:report_list')

def notifications(request):
    if request.user.is_authenticated:
        if request.user.is_superuser and not request.user.is_staff:
            notifications = Notification.objects.all().order_by('-timestamp')
        else:
            notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    elif not request.user.is_authenticated:
        messages.info(request, 'You need to be logged in to view your notifications. Please use the tabs on the navigation bar to access different pages!')
        return redirect('app:login')
    return render(request, 'notifications.html',{'notifications': notifications})


@login_required
def mark_review_in_progress(request, report):
    user = report.user if report.user else User.objects.get_or_create(username='anonymous')[0]
    Notification.objects.create(
        user=report.user,
        report=report,
        message=
        f"report #{report.id}: status changed from {report.status} to Review-In-Progress",
        timestamp=timezone.now())
    report.status = 'Review-In-Progress'
    report.report_status_changed += 1
    report.save()


@login_required
def mark_review_completed(request, report_id):
    if request.method == 'POST':
        # TO-DO: form.is_valid() and save message to admin_notes variable of report
        form = CompleteForm(request.POST)
        notes = ""
        if form.is_valid():
            notes = form.cleaned_data["message"]

        report = Report.objects.get(id=report_id)
        Notification.objects.create(
            user=report.user,
            report=report,
            message=
            f"report #{report.id}: status changed from {report.status} to Review-Completed. {admin_notes_gen(notes)}",
            timestamp=timezone.now())
        report.status = 'Review-Completed'
        report.admin_notes = notes
        report.report_status_changed += 1
        report.save()
    return redirect('app:report_list')


logger = logging.getLogger(__name__)


def admin_notes_gen(notes):
    if notes != "":
        return "Admin notes: " + notes
    else:
        return ""


def faq_view(request):
    return render(request, 'faq.html')
