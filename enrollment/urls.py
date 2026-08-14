from django.urls import path

from . import views

urlpatterns = [
    path("enroll/", views.enroll_course, name="enroll_course"),
    path("my/", views.my_enrollments, name="my_enrollments"),
    path("grade/<int:enrollment_id>/", views.grade_enrollment, name="grade_enrollment"),
    path("attendance/<int:enrollment_id>/", views.mark_attendance, name="mark_attendance"),
    path("api/enrollments/", views.enrollments_api, name="enrollments_api"),
]
