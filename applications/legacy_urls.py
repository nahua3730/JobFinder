from django.urls import path

from . import views


urlpatterns = [
    path("pipeline/", views.recruiter_pipeline),
    path("pipeline/<int:app_id>/status/", views.recruiter_update_application_status),
    path("pipeline/<int:app_id>/status-api/", views.recruiter_update_application_status_api),
]
