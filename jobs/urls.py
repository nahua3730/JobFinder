from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path('edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path("create/", views.create_job, name="create_job"),
    path('candidate-search/', views.candidate_search, name='candidate_search'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path("job/<int:job_id>/recommendations/", views.job_recommendations, name="job_recommendations"),
]
