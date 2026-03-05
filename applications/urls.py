from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path("saved-searches/", views.saved_searches, name="saved_searches"),
    path("saved-searches/<int:search_id>/run/", views.run_saved_search, name="run_saved_search"),
    path("saved-searches/<int:search_id>/delete/", views.delete_saved_search, name="delete_saved_search"),
    path("notifications/", views.notifications, name="notifications"),
]