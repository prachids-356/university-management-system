from django.contrib import messages
from django.shortcuts import redirect, render

from users.decorators import role_required
from users.models import User

from .forms import ExamForm, ExamResultForm
from .models import Exam, ExamResult


@role_required(User.Role.ADMIN, User.Role.FACULTY, User.Role.STUDENT)
def exam_list(request):
    exams = Exam.objects.select_related("course")
    return render(request, "exams/exam_list.html", {"exams": exams})


@role_required(User.Role.FACULTY, User.Role.ADMIN)
def exam_create(request):
    form = ExamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Exam created.")
        return redirect("exam_list")
    return render(request, "users/form_page.html", {"form": form, "title": "Create Exam"})


@role_required(User.Role.FACULTY, User.Role.ADMIN)
def result_entry(request):
    form = ExamResultForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Exam result saved.")
        return redirect("exam_list")
    return render(request, "users/form_page.html", {"form": form, "title": "Enter Exam Result"})


@role_required(User.Role.STUDENT)
def my_results(request):
    results = ExamResult.objects.filter(student=request.user.student_profile).select_related("exam", "exam__course")
    return render(request, "exams/my_results.html", {"results": results})
