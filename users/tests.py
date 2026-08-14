from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import StudentProfile, User


class UserFlowTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(username="stu", role=User.Role.STUDENT)
        self.student_user.set_password("pass1234")
        self.student_user.save(update_fields=["password"])
        StudentProfile.objects.create(
            user=self.student_user,
            student_id="S100",
            major="CSE",
            admission_date=date.today(),
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_auth(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
