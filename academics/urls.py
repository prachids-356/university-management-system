from django.urls import path

from . import views

urlpatterns = [
    path("courses/", views.course_list, name="course_list"),
    path("courses/new/", views.course_create, name="course_create"),
    path("courses/<int:pk>/edit/", views.course_update, name="course_update"),
    path("api/courses/", views.courses_api, name="courses_api"),
]
