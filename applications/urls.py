from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path('', views.index, name='applications.index'),
    path("jobs/<int:job_id>/apply/", views.apply_to_job, name="apply_to_job"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("my-applications/<int:app_id>/status/", views.update_application_status, name="update_status"),
]
