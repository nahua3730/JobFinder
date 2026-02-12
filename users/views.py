from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import JobSeekerProfile
from .forms import JobSeekerProfileForm
from .forms import SignUpForm
from django.contrib.auth import login as auth_login

# Create your views here.

def login_view(request):
    # We will use Django's built-in auth views later, but this maps the URL for now
    return render(request, 'users/login.html')

def logout_view(request):
    # Placeholder
    return redirect('jobs:home')

#additions for user stories 1-2 for sprint 1:
def _get_profile(user):
    profile, created = JobSeekerProfile.objects.get_or_create(user=user)
    return profile

def _get_profile(user):
    profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
    return profile

@login_required
def profile_view(request):
    profile = _get_profile(request.user)
    return render(request, "users/profile_view.html", {"profile": profile})

@login_required
def profile_edit(request):
    profile = _get_profile(request.user)

    if request.method == "POST":
        form = JobSeekerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("users:profile_view")  # ✅ this now exists
    else:
        form = JobSeekerProfileForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            # create profile automatically for non-recruiters
            if not user.is_recruiter:
                JobSeekerProfile.objects.get_or_create(user=user)

            auth_login(request, user)
            return redirect("users:profile_edit")  # redirect to profile setup
    else:
        form = SignUpForm()

    return render(request, "users/signup.html", {"form": form})