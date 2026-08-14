from django import forms

from .models import FeeInvoice


class FeeInvoiceForm(forms.ModelForm):
    class Meta:
        model = FeeInvoice
        fields = ["student", "amount", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}
