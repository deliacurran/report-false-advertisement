# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Report

def set_up_users(self):
    self.client = Client()
    self.user = User.objects.create_user(username='user', password='password')
    self.admin_user = User.objects.create_user(username='admin', password='admin!')


class ExampleTest(TestCase):
    def test_success(self):
        self.assertEqual(1 + 1, 2)


class WelcomeViewTests(TestCase):
    def test_admin_welcome_page(self):
        response = self.client.get(reverse("google_login_app:welcome"))
        self.assertContains(response, "Hello, admin")

    def test_welcome_page_disclaimer(self):
        response = self.client.get(reverse("google_login_app:welcome"))
        self.assertContains(response, "DISCLAIMER: This is NOT a real app. Please DO NOT make any reports. This website is a project for CS 3240 at UVA.")


class ReportViewTests(TestCase):
    def test_report_page_contents(self):
        response = self.client.get(reverse("google_login_app:report"))
        self.assertContains(response, "Report Submission")


class UserLoginTests(TestCase):
    def test_anonymous_user_welcome_page(self):
        response = self.client.get(reverse("google_login_app:welcome"))    
        assert response.status_code == 200
        assert 'login.html' in [t.name for t in response.templates]


 