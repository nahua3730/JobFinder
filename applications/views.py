
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from jobs.models import JobPosting
from .models import Application
from .forms import ApplicationForm

def index(request):
    return render(request, "applications/index.html")


@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)

    # Only job seekers can apply
    if not getattr(request.user, "is_job_seeker", False):
        messages.error(request, "Only job seekers can apply to jobs.")
        return redirect("jobs:home")

    existing = Application.objects.filter(job=job, applicant=request.user).first()

    if request.method == "POST":
        form = ApplicationForm(request.POST, instance=existing)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user
            if not app.status:
                app.status = Application.Status.APPLIED
            app.save()
            messages.success(request, "Application submitted!")
            return redirect("jobs:job_detail", job_id=job.id)
    else:
        form = ApplicationForm(instance=existing)

    return render(request, "applications/apply.html", {"job": job, "form": form, "application": existing})
