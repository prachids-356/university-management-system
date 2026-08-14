from django.urls import path

from . import views

urlpatterns = [
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/new/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:invoice_id>/pay/", views.pay_invoice, name="pay_invoice"),
    path("api/invoices/", views.invoices_api, name="invoices_api"),
]
