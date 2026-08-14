from datetime import date

from django.core.management.base import BaseCommand

from academics.models import Course
from users.models import FacultyProfile, StudentProfile, User


class Command(BaseCommand):
    help = "Seed baseline users, faculty, students, and courses."

    def handle(self, *args, **options):
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        if not admin_user.has_usable_password():
            admin_user.set_password("admin123")
            admin_user.save(update_fields=["password"])

        faculty_user, _ = User.objects.get_or_create(
            username="faculty1",
            defaults={"role": User.Role.FACULTY, "first_name": "Faculty"},
        )
        if not faculty_user.has_usable_password():
            faculty_user.set_password("fac123")
            faculty_user.save(update_fields=["password"])
        faculty, _ = FacultyProfile.objects.get_or_create(
            user=faculty_user,
            defaults={"employee_id": "F001", "department": "Computer Science"},
        )

        student_user, _ = User.objects.get_or_create(
            username="student1",
            defaults={"role": User.Role.STUDENT, "first_name": "Student"},
        )
        if not student_user.has_usable_password():
            student_user.set_password("stud123")
            student_user.save(update_fields=["password"])
        StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={"student_id": "S001", "major": "CSE", "admission_date": date.today()},
        )

        c1, _ = Course.objects.get_or_create(
            code="CSE100",
            defaults={"title": "Python Basics", "credits": 3, "faculty": faculty, "capacity": 40},
        )
        c2, _ = Course.objects.get_or_create(
            code="CSE200",
            defaults={"title": "OOP in Python", "credits": 4, "faculty": faculty, "capacity": 40},
        )
        c2.prerequisites.add(c1)

        self.stdout.write(self.style.SUCCESS("Seed data created/updated successfully."))
