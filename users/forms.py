from django import forms
from django.contrib.auth import get_user_model

from .models import FacultyProfile, StudentProfile

User = get_user_model()


class StudentAdmissionForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    student_id = forms.CharField(max_length=30)
    major = forms.CharField(max_length=100)
    admission_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"]
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Student ID already exists.")
        return student_id

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            **{"password": data["password"]},
            role=User.Role.STUDENT,
        )
        return StudentProfile.objects.create(
            user=user,
            student_id=data["student_id"],
            major=data["major"],
            admission_date=data["admission_date"],
        )


class FacultyOnboardForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    employee_id = forms.CharField(max_length=30)
    department = forms.CharField(max_length=100)

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"]
        if FacultyProfile.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("Employee ID already exists.")
        return employee_id

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            **{"password": data["password"]},
            role=User.Role.FACULTY,
        )
        return FacultyProfile.objects.create(
            user=user,
            employee_id=data["employee_id"],
            department=data["department"],
        )
