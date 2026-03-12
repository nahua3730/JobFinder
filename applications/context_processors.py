def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        recruiter_count = 0
        if getattr(request.user, "is_recruiter", False):
            recruiter_count = request.user.recruiter_notifications.filter(is_read=False).count()
        count += recruiter_count
        return {'unread_count': count}
    
    return {'unread_count': 0}
