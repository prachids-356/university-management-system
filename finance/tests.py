from datetime import date
from decimal import Decimal

from django.test import TestCase

from users.models import StudentProfile, User

from .models import FeeInvoice


class FinanceTests(TestCase):
    def test_mark_invoice_paid(self):
        user = User.objects.create_user(username="s1", role=User.Role.STUDENT)
        student = StudentProfile.objects.create(
            user=user,
            student_id="S500",
            major="CSE",
            admission_date=date.today(),
        )
        invoice = FeeInvoice.objects.create(
            student=student,
            amount=Decimal("1200.00"),
            due_date=date.today(),
        )
        invoice.mark_as_paid()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, FeeInvoice.Status.PAID)
        self.assertIsNotNone(invoice.paid_on)
