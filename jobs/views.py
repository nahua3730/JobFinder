from django.shortcuts import render, redirect, get_object_or_404
from .models import JobPosting
from users.models import JobSeekerProfile
from .forms import JobSearchForm, JobPostingForm, CandidateSearchForm  
from django.contrib.auth.decorators import login_required
from django.db.models import Q

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
    ''' User Story 10: Recruiter post a job '''
    if not request.user.is_recruiter:
        return redirect('jobs:home')

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            return redirect ('jobs:home')
    else:
        form = JobPostingForm()
    
    return render(request, "jobs/create_job.html", {'form': form, 'title': 'Post a New Job'})

@login_required
def edit_job(request, job_id):
    """ User Story 10: Recruiter edits a job """
    # Ensure they can only edit their OWN jobs
    job = get_object_or_404(JobPosting, id=job_id, recruiter=request.user)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('jobs:home')
    else:
        form = JobPostingForm(instance=job)
        
    return render(request, 'jobs/create_job.html', {'form': form, 'title': 'Edit Job'})

@login_required
def candidate_search(request):
    """ User Story 11: Search candidates by skills, location, projects (Could include privacy filters here)"""
    if not request.user.is_recruiter:
        return redirect('jobs:home')
        
    form = CandidateSearchForm(request.GET or None)
    candidates = JobSeekerProfile.objects.all() 

    if form.is_valid():
        query = form.cleaned_data.get('query')
        location = form.cleaned_data.get('location')
        has_projects = form.cleaned_data.get('has_projects')

        if query:
            candidates = candidates.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(skills__icontains=query)
            )
        
        if location:
            candidates = candidates.filter(location__icontains=location)
            
        if has_projects:
            # If projects aren't empty, filter by projects
            candidates = candidates.exclude(projects__exact='')
            # Optional: If they typed a keyword, check if it's inside the project text too
            if query: 
                 candidates = candidates.filter(projects__icontains=query)

    return render(request, 'jobs/candidate_search.html', {'form': form, 'candidates': candidates})
