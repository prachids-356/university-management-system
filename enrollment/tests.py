from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from academics.models import Course
from services.university_service import UniversityService
from users.models import StudentProfile, User

from .models import Enrollment


class EnrollmentServiceTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student",
            role=User.Role.STUDENT,
        )
        self.student_user.set_password("pass1234")
        self.student_user.save(update_fields=["password"])
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            student_id="S001",
            major="CSE",
            admission_date=date.today(),
        )
        self.course_1 = Course.objects.create(code="CSE100", title="Basics", credits=3, capacity=1)
        self.course_2 = Course.objects.create(code="CSE200", title="Advanced", credits=3, capacity=1)
        self.course_2.prerequisites.add(self.course_1)

    def test_prerequisite_validation(self):
        with self.assertRaises(ValidationError):
            UniversityService.validate_prerequisites(Enrollment, self.student, self.course_2)

    def test_capacity_validation(self):
        another_user = User.objects.create_user(
            username="student2",
            role=User.Role.STUDENT,
        )
        another_user.set_password("pass1234")
        another_user.save(update_fields=["password"])
        another_student = StudentProfile.objects.create(
            user=another_user,
            student_id="S002",
            major="CSE",
            admission_date=date.today(),
        )
        Enrollment.objects.create(student=another_student, course=self.course_1)
        with self.assertRaises(ValidationError):
            UniversityService.validate_capacity(self.course_1)

    def test_student_enrollment_flow(self):
        self.client.force_login(self.student_user)
        response = self.client.post(reverse("enroll_course"), {"course": self.course_1.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.course_1).exists()
        )
