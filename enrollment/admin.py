from django.contrib import admin

from .models import Attendance, Enrollment


admin.site.register(Enrollment)
admin.site.register(Attendance)
