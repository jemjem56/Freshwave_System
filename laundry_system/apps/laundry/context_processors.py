from .models import Notification

def notifications_processor(request):
    if not request.user.is_authenticated:
        return {
            'notifications':    [],
            'unread_count':     0,
            'all_notifications': [],
        }

    all_notifs    = Notification.objects.all().order_by('-created_at')
    unread_notifs = Notification.objects.filter(is_read=False).order_by('-created_at')

    return {
        'notifications':     unread_notifs[:10],      # Bell shows unread only by default
        'all_notifications': all_notifs[:30],          # All tab
        'unread_count':      unread_notifs.count(),    # Badge number
    }