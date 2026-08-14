from django.db import models
from django.utils import timezone

from users.models import StudentProfile


class FeeInvoice(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date"]

    def mark_as_paid(self):
        self.status = self.Status.PAID
        self.paid_on = timezone.now().date()
        self.save(update_fields=["status", "paid_on", "updated_at"])
