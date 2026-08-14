from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import role_required
from users.models import User

from .forms import CourseForm
from .models import Course


@role_required(User.Role.ADMIN, User.Role.FACULTY, User.Role.STUDENT)
def course_list(request):
    courses = Course.objects.select_related("faculty__user").prefetch_related("prerequisites")
    return render(request, "academics/course_list.html", {"courses": courses})


@role_required(User.Role.ADMIN)
def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course created successfully.")
        return redirect("course_list")
    return render(request, "users/form_page.html", {"form": form, "title": "Create Course"})


@role_required(User.Role.ADMIN)
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course updated successfully.")
        return redirect("course_list")
    return render(request, "users/form_page.html", {"form": form, "title": "Update Course"})


@role_required(User.Role.ADMIN, User.Role.FACULTY, User.Role.STUDENT)
def courses_api(request):
    data = [
        {
            "code": course.code,
            "title": course.title,
            "credits": course.credits,
            "capacity": course.capacity,
            "faculty": course.faculty.user.get_full_name() if course.faculty else None,
        }
        for course in Course.objects.select_related("faculty__user")
    ]
    return JsonResponse({"results": data})
