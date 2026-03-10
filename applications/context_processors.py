def unread_notifications(request):
    """Makes the unread notification count available to all templates."""
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_count': count}
    
    return {'unread_count': 0}