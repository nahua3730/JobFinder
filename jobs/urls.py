from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_job, name='create_job'),
    path("search/", views.search, name="search"),
    path('edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('candidate-search/', views.candidate_search, name='candidate_search'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path("<int:job_id>/", views.job_detail, name="job_detail"),
    path("recommended/", views.recommended_jobs, name="recommended_jobs"),
    path("map/", views.job_map, name="job_map"),
    path("map-data/", views.job_map_data, name="job_map_data"),
    path('<int:job_id>/applications/', views.job_applications, name='job_applications'),
]
