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
    path("job/<int:job_id>/recommendations/", views.job_recommendations, name="job_recommendations"),
    path("recruiter/geocode-search/", views.recruiter_geocode_search, name="recruiter_geocode_search"),
    path("recruiter/reverse-geocode/", views.recruiter_reverse_geocode, name="recruiter_reverse_geocode"),
    path("recruiter/jobs/<int:job_id>/applicant-map/", views.recruiter_applicant_map, name="recruiter_applicant_map"),
    path("recruiter/jobs/<int:job_id>/applicant-map-data/", views.recruiter_applicant_map_data, name="recruiter_applicant_map_data"),
]