from apps.laundry.models import Notification


def mark_notification_as_read(notification):
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return notification


def mark_all_notifications_as_read():
    Notification.objects.filter(is_read=False).update(is_read=True)
    return "All notifications marked as read."


def delete_notification(notification):
    notification.delete()
    return "Notification deleted."


def delete_all_notifications():
    Notification.objects.all().delete()
    return "All notifications deleted."