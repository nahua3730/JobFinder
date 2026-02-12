from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_job, name='create_job'),
    path('search/', views.candidate_search, name='candidate_search'),
    path("recommended/", views.recommended_jobs, name="recommended_jobs"),
]