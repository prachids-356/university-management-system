from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FacultyProfile, StudentProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")


admin.site.register(StudentProfile)
admin.site.register(FacultyProfile)
