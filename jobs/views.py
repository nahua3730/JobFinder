from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JobPosting
from users.models import JobSeekerProfile
# You will need to create a JobForm in forms.py
# from .forms import JobForm 
# Insert your views here.

def home(request):
    """
    Public homepage / Job list for Seekers (Story 2)
    """
    jobs = JobPosting.objects.all().order_by('-created_at')
    return render(request, 'jobs/index.html', {'jobs': jobs})

@login_required
def create_job(request):
    """
    User Story 10: Post a job (Recruiter only)
    """
    if not request.user.is_recruiter:
        return redirect('jobs:home')
        
    if request.method == 'POST':
        # form = JobForm(request.POST)
        # if form.is_valid():
        #     job = form.save(commit=False)
        #     job.recruiter = request.user
        #     job.save()
        #     return redirect('jobs:home')
        pass
    else:
        # form = JobForm()
        pass
    
    return render(request, 'jobs/create_job.html') # You need to create this template

@login_required
def candidate_search(request):
    """
    User Story 11: Search candidates (Recruiter only)
    """
    if not request.user.is_recruiter:
        return redirect('jobs:home')
        
    query = request.GET.get('q')
    results = []
    if query:
        # Simple search implementation
        results = JobSeekerProfile.objects.filter(skills__icontains=query)
        
    return render(request, 'jobs/candidate_search.html', {'results': results})

@login_required
def recommended_jobs(request):
    if not request.user.is_job_seeker:
        return redirect("jobs:home")
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    user_skills = {
        s.strip().lower()
        for s in (profile.skills or "").split(",")
        if s.strip()
    }
    jobs = JobPosting.objects.all().order_by("-created_at")
    recommended = [] 
    for job in jobs:
        job_skills = {
            s.strip().lower()
            for s in (getattr(job, "skills", "") or "").split(",")
            if s.strip()
        }
        score = len(user_skills & job_skills)
        if score > 0:
            recommended.append((job, score))
    recommended.sort(key=lambda pair: pair[1], reverse=True)
    return render(request, "jobs/recommended_jobs.html", {
        "recommended": recommended,
        "user_skills": sorted(user_skills),
    })