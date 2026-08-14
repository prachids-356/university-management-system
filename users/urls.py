from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("admissions/student/", views.admit_student, name="admit_student"),
    path("admissions/faculty/", views.onboard_faculty, name="onboard_faculty"),
    path("reports/", views.reports_view, name="reports"),
]
