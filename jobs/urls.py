from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("create/", views.create_job, name="create_job"),
]
