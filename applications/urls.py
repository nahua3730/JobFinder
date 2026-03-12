from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path('', views.index, name='applications.index'),
    path("jobs/<int:job_id>/apply/", views.apply_to_job, name="apply_to_job"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("my-applications/<int:app_id>/status/", views.update_application_status, name="update_status"),
    path("my-applications/<int:app_id>/status-api/", views.update_application_status_api, name="update_status_api"),
    path("recruiter/pipeline/", views.recruiter_pipeline, name="recruiter_pipeline"),
    path("recruiter/pipeline/<int:app_id>/status/", views.recruiter_update_application_status, name="recruiter_update_application_status"),
    path("recruiter/pipeline/<int:app_id>/status-api/", views.recruiter_update_application_status_api, name="recruiter_update_application_status_api"),
    path("saved-searches/", views.saved_searches, name="saved_searches"),
    path("saved-searches/<int:search_id>/run/", views.run_saved_search, name="run_saved_search"),
    path("saved-searches/<int:search_id>/delete/", views.delete_saved_search, name="delete_saved_search"),
    path("notifications/", views.notifications, name="notifications"),
    path('notifications/mark-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/<int:notif_id>/read/', views.read_notification, name='read_notification'),
    path('notifications/<int:notif_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/recruiter/<int:notif_id>/read/', views.read_recruiter_notification, name='read_recruiter_notification'),
    path('notifications/recruiter/<int:notif_id>/delete/', views.delete_recruiter_notification, name='delete_recruiter_notification'),
    path("messages/inbox/", views.inbox, name="inbox"),
    path("messages/sent/", views.sent_messages, name="sent_messages"),
    path("messages/compose/<int:user_id>/", views.compose_message, name="compose_message"),
    path("messages/email/<int:user_id>/", views.compose_email, name="compose_email"),
]
