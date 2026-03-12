from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import JobSeekerProfile
from .models import User
from .models import RecruiterProfile
from .forms import JobSeekerProfileForm
from .forms import SignUpForm
from django.contrib.auth import login as auth_login
from .forms import PrivacySettingsForm
from .forms import RecruiterUserForm, RecruiterProfileForm
from jobs.geocoding import geocode_us
from django.contrib import messages
from django.urls import reverse
from applications.models import Notification
from jobs.models import JobPosting

def login_view(request):
    return render(request, 'users/login.html')

def logout_view(request):
    return redirect('jobs:home')

def _get_profile(user):
    if not user.is_job_seeker:
        return None
    profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
    return profile

@login_required
def profile_view(request):
    if not request.user.is_job_seeker:
        return redirect("users:recruiter_profile")
    profile = _get_profile(request.user)
    return render(request, "users/profile_view.html", {"profile": profile, "is_owner": True})

@login_required
def profile_edit(request):
    if not request.user.is_job_seeker:
        return redirect("users:recruiter_profile")
    profile = _get_profile(request.user)

    if request.method == "POST":
        form = JobSeekerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)

            profile.location = profile.build_location_display()
            q = profile.build_geocode_query()

            if q:
                coords = geocode_us(q)
                if coords:
                    profile.latitude, profile.longitude = coords
                    
            form.save()
            
            if profile.skills:
                seeker_skills = {s.strip().lower() for s in profile.skills.split(",") if s.strip()}
                
                active_jobs = JobPosting.objects.filter(status=JobPosting.Status.APPROVED).exclude(skills="")
                
                for job in active_jobs:
                    job_skills = {s.strip().lower() for s in job.skills.split(",") if s.strip()}
                    
                    if seeker_skills.intersection(job_skills):
                        Notification.objects.get_or_create(
                            recipient=request.user,
                            message=f"New Match! '{job.title}' requires your skills.",
                            link=reverse("jobs:job_detail", args=[job.id])
                        )

            return redirect("users:profile_view")  
    else:
        form = JobSeekerProfileForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            role = request.POST.get("role")
            user.is_recruiter = role == "recruiter"
            user.is_job_seeker = role != "recruiter"
            user.save()

            if user.is_recruiter:
                RecruiterProfile.objects.get_or_create(
                    user=user,
                    defaults={"company_name": "Pending Company"}
                )
                auth_login(request, user)
                return redirect("users:recruiter_profile_edit") 
            else:
                JobSeekerProfile.objects.get_or_create(user=user)
                auth_login(request, user)
                return redirect("users:profile_edit")

    else:
        form = SignUpForm()

    return render(request, "users/signup.html", {"form": form})
@login_required
def privacy_settings(request):
    if not request.user.is_job_seeker:
        return redirect("users:recruiter_profile")
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = PrivacySettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Privacy settings saved successfully.")
            return redirect("users:privacy_settings")
    else:
        form = PrivacySettingsForm(instance=profile)
    skills_list = [s.strip() for s in (profile.skills or "").split(",") if s.strip()]
    return render(request, "users/privacy_settings.html", {"form": form, "profile": profile,
        "skills_list": skills_list,})

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    if not user.is_job_seeker:
        return render(request, "users/not_found.html", status=404)
    profile = _get_profile(user)
    is_owner = request.user.is_authenticated and request.user == user
    return render(request, "users/profile_view.html", {"profile": profile, "is_owner": is_owner})

@login_required
def recruiter_profile(request):
    if not request.user.is_recruiter:
        return redirect("users:profile_view")
    profile, _ = RecruiterProfile.objects.get_or_create(
        user=request.user, defaults={"company_name": ""}
    )
    return render(request, "users/recruiter_profile.html", {"profile": profile})
@login_required
def recruiter_profile_edit(request):
    if not request.user.is_recruiter:
        return redirect("users:profile_view")

    profile, _ = RecruiterProfile.objects.get_or_create(
        user=request.user, defaults={"company_name": ""}
    )

    if request.method == "POST":
        user_form = RecruiterUserForm(request.POST, instance=request.user)
        profile_form = RecruiterProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("users:recruiter_profile")
    else:
        user_form = RecruiterUserForm(instance=request.user)
        profile_form = RecruiterProfileForm(instance=profile)

    return render(request, "users/recruiter_profile_edit.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })
def enter_page(request):
    return render(request, "users/enter.html")
