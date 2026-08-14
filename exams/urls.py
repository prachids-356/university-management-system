from django.urls import path

from . import views

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("new/", views.exam_create, name="exam_create"),
    path("results/new/", views.result_entry, name="result_entry"),
    path("results/my/", views.my_results, name="my_results"),
]
