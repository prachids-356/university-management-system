from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from academics.models import Course
from enrollment.models import Enrollment
from finance.models import FeeInvoice

from .decorators import role_required
from .forms import FacultyOnboardForm, StudentAdmissionForm
from .models import FacultyProfile, StudentProfile, User


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required
def dashboard(request):
    context = {"role": request.user.role}
    if request.user.role == User.Role.ADMIN:
        context.update(
            {
                "students": StudentProfile.objects.count(),
                "faculty": FacultyProfile.objects.count(),
                "courses": Course.objects.count(),
                "pending_invoices": FeeInvoice.objects.filter(status=FeeInvoice.Status.PENDING).count(),
            }
        )
        return render(request, "users/dashboard_admin.html", context)

    if request.user.role == User.Role.FACULTY:
        faculty = request.user.faculty_profile
        courses = Course.objects.filter(faculty=faculty).annotate(enrollment_count=Count("enrollments"))
        context["courses"] = courses
        return render(request, "users/dashboard_faculty.html", context)

    student = request.user.student_profile
    context["enrollments"] = Enrollment.objects.filter(student=student).select_related("course")
    return render(request, "users/dashboard_student.html", context)


@role_required(User.Role.ADMIN)
def admit_student(request):
    form = StudentAdmissionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student admitted successfully.")
        return redirect("dashboard")
    return render(request, "users/form_page.html", {"form": form, "title": "Admit Student"})


@role_required(User.Role.ADMIN)
def onboard_faculty(request):
    form = FacultyOnboardForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Faculty onboarded successfully.")
        return redirect("dashboard")
    return render(request, "users/form_page.html", {"form": form, "title": "Onboard Faculty"})


@role_required(User.Role.ADMIN)
def reports_view(request):
    top_courses = (
        Course.objects.annotate(total=Count("enrollments")).order_by("-total", "code")[:5]
    )
    context = {
        "top_courses": top_courses,
        "paid_invoices": FeeInvoice.objects.filter(status=FeeInvoice.Status.PAID).count(),
        "pending_invoices": FeeInvoice.objects.filter(status=FeeInvoice.Status.PENDING).count(),
    }
    return render(request, "users/reports.html", context)
