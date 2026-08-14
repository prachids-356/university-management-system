from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from academics.models import Course
from services.university_service import UniversityService
from users.decorators import role_required
from users.models import User

from .forms import AttendanceForm, EnrollmentForm, GradeForm
from .models import Enrollment


@role_required(User.Role.STUDENT)
def enroll_course(request):
    form = EnrollmentForm(
        request.POST or None,
        course_queryset=Course.objects.all(),
    )
    if request.method == "POST" and form.is_valid():
        course = form.cleaned_data["course"]
        student = request.user.student_profile
        try:
            UniversityService.validate_student_role(request.user)
            UniversityService.validate_duplicate(Enrollment, student, course)
            UniversityService.validate_capacity(course)
            UniversityService.validate_prerequisites(Enrollment, student, course)
            Enrollment.objects.create(student=student, course=course)
            messages.success(request, "Enrollment completed.")
            return redirect("my_enrollments")
        except ValidationError as exc:
            form.add_error("course", exc.message)
    return render(request, "users/form_page.html", {"form": form, "title": "Enroll in Course"})


@role_required(User.Role.STUDENT)
def my_enrollments(request):
    enrollments = Enrollment.objects.filter(student=request.user.student_profile).select_related("course")
    return render(request, "enrollment/my_enrollments.html", {"enrollments": enrollments})


@role_required(User.Role.FACULTY)
def grade_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        course__faculty=request.user.faculty_profile,
    )
    form = GradeForm(request.POST or None, instance=enrollment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grade updated successfully.")
        return redirect("dashboard")
    return render(request, "users/form_page.html", {"form": form, "title": "Update Grade"})


@role_required(User.Role.FACULTY)
def mark_attendance(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        course__faculty=request.user.faculty_profile,
    )
    form = AttendanceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        attendance = form.save(commit=False)
        attendance.enrollment = enrollment
        attendance.save()
        messages.success(request, "Attendance recorded successfully.")
        return redirect("dashboard")
    return render(request, "users/form_page.html", {"form": form, "title": "Mark Attendance"})


@role_required(User.Role.ADMIN, User.Role.FACULTY, User.Role.STUDENT)
def enrollments_api(request):
    enrollments = Enrollment.objects.select_related("student__user", "course")
    data = [
        {
            "student": item.student.student_id,
            "student_name": item.student.user.get_full_name(),
            "course": item.course.code,
            "status": item.status,
            "grade": item.grade,
        }
        for item in enrollments
    ]
    return JsonResponse({"results": data})
