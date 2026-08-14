from django import forms

from .models import Exam, ExamResult


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["course", "title", "exam_date", "total_marks"]
        widgets = {"exam_date": forms.DateInput(attrs={"type": "date"})}


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ["exam", "student", "obtained_marks"]
