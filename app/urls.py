from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('faq/', views.faq_view, name='faq'),
    path("report/", views.report, name="report"),
    path("login/", views.login, name="login"),
    path("logout/", views.logOut, name="logOut"),
    path("signup/", views.signUp, name="signup"),
    path('reports/', views.report_list, name='report_list'),
    path("report_success/", views.report_success, name="report_success"),
    path("notifications/", views.notifications, name="notifications"),
    path('mark_review_in_progress/<int:report_id>/', views.mark_review_in_progress, name='mark_review_in_progress'),
    path('mark_review_completed/<int:report_id>/', views.mark_review_completed, name='mark_review_completed'),
    path('reports/<uuid:report_uuid>/',views.report_detail,name='report_detail'),
    path('delete_report/<uuid:report_uuid>/', views.delete_report, name='delete_report'),
]
