from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("profile/", views.profile_view, name="profile_view"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("privacy/", views.privacy_settings, name="privacy_settings"),
    path("profile/<str:username>/", views.profile_detail, name="profile_detail"),
    path("recruiter/profile/", views.recruiter_profile, name="recruiter_profile"),
    path("recruiter/profile/edit/", views.recruiter_profile_edit, name="recruiter_profile_edit"),
]