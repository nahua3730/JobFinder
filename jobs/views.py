from django.shortcuts import render, redirect, get_object_or_404
from .models import JobPosting
from users.models import JobSeekerProfile
from .forms import JobSearchForm, JobPostingForm, CandidateSearchForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .geocoding import geocode_us

def home(request):
    if request.user.is_authenticated and request.user.is_recruiter:
        return redirect("jobs:my_jobs")
    jobs = JobPosting.objects.all().order_by('-created_at')
    return render(request, "jobs/index.html", {"jobs": jobs})

def search(request):
    if request.user.is_authenticated and request.user.is_recruiter:
        return redirect("jobs:my_jobs")

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
            jobs = jobs.filter(max_salary__gte=salary_min)
        if salary_max is not None:
            jobs = jobs.filter(min_salary__lte=salary_max)

        if is_remote:
            v = str(is_remote).strip().lower()
            if v in ("remote", "true", "1", "yes"):
                jobs = jobs.filter(is_remote=True)
            elif v in ("on-site", "onsite", "false", "0", "no"):
                jobs = jobs.filter(is_remote=False)

        if visa_sponsorship:
            jobs = jobs.filter(visa_sponsorship=True)

    return render(request, "jobs/search.html", {"form": form, "jobs": jobs})

def _filtered_jobs_from_search_form(request):
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
            jobs = jobs.filter(max_salary__gte=salary_min)
        if salary_max is not None:
            jobs = jobs.filter(min_salary__lte=salary_max)

        if is_remote:
            v = str(is_remote).strip().lower()
            if v in ("remote", "true", "1", "yes"):
                jobs = jobs.filter(is_remote=True)
            elif v in ("on-site", "onsite", "false", "0", "no"):
                jobs = jobs.filter(is_remote=False)

        if visa_sponsorship:
            jobs = jobs.filter(visa_sponsorship=True)

    return form, jobs


def job_map(request):
    if request.user.is_authenticated and request.user.is_recruiter:
        return redirect("jobs:my_jobs")

    form, _ = _filtered_jobs_from_search_form(request)

    default_radius = 10
    if request.user.is_authenticated and getattr(request.user, "is_job_seeker", False):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        default_radius = getattr(profile, "preferred_commute_radius_miles", 10) or 10

    home_lat = None
    home_lng = None
    home_label = None

    if request.user.is_authenticated and getattr(request.user, "is_job_seeker", False):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        home_lat = profile.latitude
        home_lng = profile.longitude
        home_label = profile.location

    return render(request, "jobs/map.html", {
        "form": form,
        "default_radius": default_radius,
        "home_lat": home_lat,
        "home_lng": home_lng,
        "home_label": home_label,
    })

def job_map_data(request):
    if request.user.is_authenticated and request.user.is_recruiter:
        return JsonResponse({"error": "Recruiters do not use this endpoint."}, status=403)

    _, jobs = _filtered_jobs_from_search_form(request)

    jobs = jobs.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    data = []
    for job in jobs:
        data.append({
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "latitude": job.latitude,
            "longitude": job.longitude,
            "is_remote": job.is_remote,
        })

    return JsonResponse(data, safe=False)

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
            job.location = job.build_location_string()

            if job.is_remote:
                job.latitude = None
                job.longitude = None
            else:
                coords = geocode_us(job.location)
                if coords:
                    job.latitude, job.longitude = coords

            job.save()
            return redirect('jobs:home')
    else:
        form = JobPostingForm()

    return render(request, "jobs/create_job.html", {'form': form, 'title': 'Post a New Job'})

@login_required
def edit_job(request, job_id):
    """ User Story 10: Recruiter edits a job """
    job = get_object_or_404(JobPosting, id=job_id, recruiter=request.user)
    old_location = job.location
    old_remote = job.is_remote

    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)

            job.location = job.build_location_string()

            location_changed = (job.location != old_location)
            remote_changed = (job.is_remote != old_remote)
            coords_missing = (job.latitude is None or job.longitude is None)

            if job.is_remote:
                job.latitude = None
                job.longitude = None
            elif location_changed or remote_changed or coords_missing:
                coords = geocode_us(job.location)
                if coords:
                    job.latitude, job.longitude = coords

            job.save()
            return redirect('jobs:home')
    else:
        form = JobPostingForm(instance=job)

    return render(request, 'jobs/create_job.html', {'form': form, 'title': 'Edit Job'})

@login_required
def candidate_search(request):
    """ User Story 11: Search candidates by skills, location, projects (respects privacy) """
    if not request.user.is_recruiter:
        return redirect("jobs:home")

    form = CandidateSearchForm(request.GET or None)
    candidates = JobSeekerProfile.objects.filter(
        user__is_job_seeker=True,
        privacy_enabled=False,
    )

    if form.is_valid():
        query = form.cleaned_data.get("query")
        location = form.cleaned_data.get("location")
        has_projects = form.cleaned_data.get("has_projects")

        if query:
            q_obj = Q(
                user__first_name__icontains=query
            ) | Q(
                user__last_name__icontains=query
            )

            q_obj |= Q(show_skills=True, skills__icontains=query)
            q_obj |= Q(show_projects=True, projects__icontains=query)

            candidates = candidates.filter(q_obj)

        if location:
            candidates = candidates.filter(show_location=True, location__icontains=location)

        if has_projects:
            candidates = candidates.filter(show_projects=True).exclude(projects__exact="")

    return render(request, "jobs/candidate_search.html", {"form": form, "candidates": candidates})

@login_required
def my_jobs(request):
    """ Show only the jobs created by the logged-in recruiter """
    if not request.user.is_recruiter:
        return redirect('jobs:home')

    my_job_list = JobPosting.objects.filter(recruiter=request.user).order_by('-created_at')
    return render(request, 'jobs/my_jobs.html', {'jobs': my_job_list})

def job_detail(request, job_id):
    if request.user.is_authenticated and request.user.is_recruiter:
        return redirect("jobs:my_jobs")

    job = get_object_or_404(JobPosting, id=job_id)
    return render(request, "jobs/job_detail.html", {"job": job})

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
