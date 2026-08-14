from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import role_required
from users.models import User

from .forms import FeeInvoiceForm
from .models import FeeInvoice


@role_required(User.Role.ADMIN, User.Role.STUDENT)
def invoice_list(request):
    invoices = FeeInvoice.objects.select_related("student__user")
    if request.user.role == User.Role.STUDENT:
        invoices = invoices.filter(student=request.user.student_profile)
    return render(request, "finance/invoice_list.html", {"invoices": invoices})


@role_required(User.Role.ADMIN)
def invoice_create(request):
    form = FeeInvoiceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Fee invoice created.")
        return redirect("invoice_list")
    return render(request, "users/form_page.html", {"form": form, "title": "Create Invoice"})


@role_required(User.Role.STUDENT)
def pay_invoice(request, invoice_id):
    invoice = get_object_or_404(FeeInvoice, id=invoice_id, student=request.user.student_profile)
    invoice.mark_as_paid()
    messages.success(request, "Invoice marked as paid.")
    return redirect("invoice_list")


@role_required(User.Role.ADMIN, User.Role.STUDENT)
def invoices_api(request):
    invoices = FeeInvoice.objects.select_related("student__user")
    if request.user.role == User.Role.STUDENT:
        invoices = invoices.filter(student=request.user.student_profile)
    return JsonResponse(
        {
            "results": [
                {
                    "student_id": invoice.student.student_id,
                    "amount": str(invoice.amount),
                    "due_date": invoice.due_date.isoformat(),
                    "status": invoice.status,
                }
                for invoice in invoices
            ]
        }
    )
