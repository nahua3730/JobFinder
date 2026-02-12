from django.shortcuts import render
from .models import JobPosting
from .forms import JobSearchForm 
from users.models import JobSeekerProfile   
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def home(request):
    # landing page only
    return render(request, "jobs/home.html")


def search(request):
    form = JobSearchForm(request.GET or None)
    jobs = JobPosting.objects.all().order_by("-created_at")

    if form.is_valid():
        title = form.cleaned_data.get("title")
        skills = form.cleaned_data.get("skills")
        location = form.cleaned_data.get("location")
        salary_min = form.cleaned_data.get("salary_min")
        salary_max = form.cleaned_data.get("salary_max")
        is_remote = form.cleaned_data.get("is_remote")
        visa_sponsorship = form.cleaned_data.get("visa_sponsorship")

        if title:
            jobs = jobs.filter(title__icontains=title)
        if skills:
            jobs = jobs.filter(skills__icontains=skills)
        if location:
            jobs = jobs.filter(location__icontains=location)

        if salary_min is not None:
            jobs = jobs.filter(min_salary__gte=salary_min)
        if salary_max is not None:
            jobs = jobs.filter(max_salary__lte=salary_max)

        if is_remote != "":
            jobs = jobs.filter(is_remote=is_remote)

        if visa_sponsorship:
            jobs = jobs.filter(visa_sponsorship=True)

    return render(request, "jobs/search.html", {"form": form, "jobs": jobs})

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
