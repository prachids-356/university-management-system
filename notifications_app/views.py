from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import role_required
from users.models import User

from .models import Notification


@role_required(User.Role.ADMIN, User.Role.FACULTY, User.Role.STUDENT)
def notification_list(request):
    items = Notification.objects.filter(user=request.user)
    return render(request, "notifications/list.html", {"notifications": items})


@role_required(User.Role.ADMIN, User.Role.FACULTY, User.Role.STUDENT)
def mark_notification_read(request, notification_id):
    item = get_object_or_404(Notification, id=notification_id, user=request.user)
    item.is_read = True
    item.save(update_fields=["is_read", "updated_at"])
    return redirect("notification_list")
