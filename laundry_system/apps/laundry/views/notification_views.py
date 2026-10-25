from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.laundry.models import Notification
from apps.laundry.services.notification_service import (
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification as delete_notification_service,
    delete_all_notifications as delete_all_notifications_service,
)


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    mark_notification_as_read(notification)
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def mark_all_read(request):
    if request.method == "POST":
        success_message = mark_all_notifications_as_read()
        messages.success(request, success_message)

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if request.method == "POST":
        success_message = delete_notification_service(notification)
        messages.success(request, success_message)
        return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect(request.META.get("HTTP_REFERER", "/"))
    

@login_required
def delete_all_notifications(request):
    if request.method == "POST":
        success_message = delete_all_notifications_service()
        messages.success(request, success_message)
        return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect(request.META.get("HTTP_REFERER", "/"))