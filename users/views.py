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
# Create your views here.

def login_view(request):
    # We will use Django's built-in auth views later, but this maps the URL for now
    return render(request, 'users/login.html')

def logout_view(request):
    # Placeholder
    return redirect('jobs:home')

#additions for user stories 1-2 for sprint 1:
def _get_profile(user):
    if not user.is_job_seeker:
        return None
    profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
    return profile

@login_required
def profile_view(request):
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
            form.save()
            return redirect("users:profile_view")  
    else:
        form = JobSeekerProfileForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_recruiter:
                user.is_job_seeker = False
            else:
                user.is_job_seeker = True
            user.save()

            if not user.is_recruiter:
                JobSeekerProfile.objects.get_or_create(user=user)
            user = form.save(commit=False)

            is_recruiter = form.cleaned_data.get('is_recruiter')

            # create profile automatically for non-recruiters
            if is_recruiter:
                user.is_recruiter = True
                user.is_job_seeker = False
            else:
                user.is_recruiter = False
                user.is_job_seeker = True
            
            user.save()

            if user.is_recruiter:
                RecruiterProfile.objects.create(user=user, company_name="Pending Company")
            else:
                JobSeekerProfile.objects.create(user=user)
                
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
            return redirect("users:profile_view") 
    else:
        form = PrivacySettingsForm(instance=profile)
    return render(request, "users/privacy_settings.html", {"form": form})

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    if not user.is_job_seeker:
        return render(request, "users/not_found.html", status=404)
    profile = _get_profile(user)
    is_owner = request.user.is_authenticated and request.user == user
    return render(request, "users/profile_view.html", {"profile": profile, "is_owner": is_owner})

@login_required
def candidate_list(request):
    if not request.user.is_recruiter:
        return redirect("users:profile_view")
    candidates = User.objects.filter(is_job_seeker=True).order_by("username")
    return render(request, "users/candidate_list.html", {"candidates": candidates})

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