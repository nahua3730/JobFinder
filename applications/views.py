
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch
from jobs.models import JobPosting
from .models import Application
from .forms import ApplicationForm, ApplicationStatusForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Application
from .forms import ApplicationStatusForm
def index(request):
    return render(request, "applications/index.html")


@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)

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

@login_required
def my_applications(request):
    if not getattr(request.user, "is_job_seeker", False):
        return redirect("jobs:home")

    apps = (
        Application.objects.filter(applicant=request.user)
        .select_related("job")
        .order_by("-updated_at")
    )
    return render(request, "applications/my_applications.html", {"applications": apps})


@login_required
def update_application_status(request, app_id):
    if not getattr(request.user, "is_job_seeker", False):
        return redirect("jobs:home")

    app = get_object_or_404(Application, id=app_id, applicant=request.user)

    if request.method == "POST":
        form = ApplicationStatusForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, "Application status updated!")
            return redirect("applications:my_applications")
    else:
        form = ApplicationStatusForm(instance=app)

    return render(request, "applications/update_status.html", {"application": app, "form": form})

@login_required
def recruiter_pipeline(request):
    if not getattr(request.user, "is_recruiter", False):
        return redirect("jobs:home")

    qs = (
        Application.objects
        .filter(job__recruiter=request.user)
        .select_related("job", "applicant", "applicant__seeker_profile")
        .order_by("-updated_at")
    )

    columns = {
        "Applied": qs.filter(status=Application.Status.APPLIED),
        "Review": qs.filter(status=Application.Status.REVIEW),
        "Interview": qs.filter(status=Application.Status.INTERVIEW),
        "Offer": qs.filter(status=Application.Status.OFFER),
        "Closed": qs.filter(status=Application.Status.CLOSED),
    }

    return render(request, "applications/recruiter_pipeline.html", {"columns": columns})

@login_required
def recruiter_update_application_status(request, app_id):
    if not getattr(request.user, "is_recruiter", False):
        return redirect("jobs:home")

    app = get_object_or_404(Application, id=app_id, job__recruiter=request.user)

    if request.method == "POST":
        form = ApplicationStatusForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate moved in pipeline.")
            return redirect("applications:recruiter_pipeline")
    else:
        form = ApplicationStatusForm(instance=app)

    return render(request, "applications/recruiter_update_status.html", {"application": app, "form": form})

@require_POST
@login_required
def recruiter_update_application_status_api(request, app_id):
    if not getattr(request.user, "is_recruiter", False):
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)

    app = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    new_status = request.POST.get("status")
    valid = {choice[0] for choice in Application.Status.choices}

    if new_status not in valid:
        return JsonResponse({"ok": False, "error": "invalid status"}, status=400)

    app.status = new_status
    app.save(update_fields=["status", "updated_at"])
    return JsonResponse({"ok": True})