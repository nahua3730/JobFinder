from django.shortcuts import render
from .models import JobPosting
from .forms import JobSearchForm  
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
    # Temporary placeholder so the URL + navbar link doesn't crash.
    return render(request, "jobs/create_job.html")
