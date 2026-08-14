from django import forms

from academics.models import Course

from .models import Attendance, Enrollment


class EnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.none())

    def __init__(self, *args, **kwargs):
        course_queryset = kwargs.pop("course_queryset", Course.objects.all())
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = course_queryset


class GradeForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["status", "grade"]


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["date", "status"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
