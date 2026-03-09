from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q

from jobs.models import JobPosting
from users.models import JobSeekerProfile
from .models import (
    Application,
    SavedCandidateSearch,
    SavedSearchSeenCandidate,
    RecruiterNotification,
)
from .forms import ApplicationForm, ApplicationStatusForm


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

    return render(request, "applications/apply.html", {
        "job": job,
        "form": form,
        "application": existing,
    })


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

    return render(request, "applications/update_status.html", {
        "application": app,
        "form": form,
    })


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

    return render(request, "applications/recruiter_update_status.html", {
        "application": app,
        "form": form,
    })


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


def _apply_candidate_filters(filters):
    """
    Reuse candidate search logic + enforce privacy.
    filters: dict with keys query/location/has_projects
    """
    query = (filters.get("query") or "").strip()
    location = (filters.get("location") or "").strip()
    has_projects = bool(filters.get("has_projects"))

    candidates = JobSeekerProfile.objects.filter(
        user__is_job_seeker=True,
        privacy_enabled=False,
    )

    if query:
        candidates = candidates.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(skills__icontains=query)
        )

    if location:
        candidates = candidates.filter(location__icontains=location)

    if has_projects:
        candidates = candidates.exclude(projects__exact="")
        if query:
            candidates = candidates.filter(projects__icontains=query)

    return candidates


def _filters_to_querystring(filters):
    parts = []
    if filters.get("query"):
        parts.append(f'query={filters["query"]}')
    if filters.get("location"):
        parts.append(f'location={filters["location"]}')
    if filters.get("has_projects"):
        parts.append("has_projects=on")
    return "&".join(parts)


def _refresh_saved_search_notifications(recruiter):
    """
    On-demand notification generation:
    - For each active saved search, re-run query
    - Find candidates not seen before
    - Create one notification with the count
    - Mark candidates as seen
    """
    saved_searches = SavedCandidateSearch.objects.filter(
        recruiter=recruiter,
        is_active=True
    )

    for ss in saved_searches:
        candidates_qs = _apply_candidate_filters(ss.filters).select_related("user")

        new_candidate_users = []
        for prof in candidates_qs:
            exists = SavedSearchSeenCandidate.objects.filter(
                saved_search=ss,
                candidate_user=prof.user
            ).exists()
            if not exists:
                new_candidate_users.append(prof.user)

        if new_candidate_users:
            count = len(new_candidate_users)
            title = f'New matches for "{ss.name or "Saved Search"}"'
            body = f"{count} new candidate(s) match your saved search."
            url = "/candidate-search/?" + _filters_to_querystring(ss.filters)

            RecruiterNotification.objects.create(
                user=recruiter,
                title=title,
                body=body,
                url=url,
            )

            SavedSearchSeenCandidate.objects.bulk_create(
                [
                    SavedSearchSeenCandidate(saved_search=ss, candidate_user=u)
                    for u in new_candidate_users
                ],
                ignore_conflicts=True,
            )

        ss.last_checked_at = timezone.now()
        ss.save(update_fields=["last_checked_at"])


@login_required
def saved_searches(request):
    if not request.user.is_recruiter:
        return redirect("jobs:home")

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        query = (request.POST.get("query") or "").strip()
        location = (request.POST.get("location") or "").strip()
        has_projects = bool(request.POST.get("has_projects"))

        filters = {
            "query": query,
            "location": location,
            "has_projects": has_projects,
        }

        SavedCandidateSearch.objects.create(
            recruiter=request.user,
            name=name,
            filters=filters,
        )
        return redirect("applications:saved_searches")

    _refresh_saved_search_notifications(request.user)

    searches = SavedCandidateSearch.objects.filter(
        recruiter=request.user
    ).order_by("-created_at")

    return render(request, "applications/saved_searches.html", {"searches": searches})


@login_required
def run_saved_search(request, search_id):
    if not request.user.is_recruiter:
        return redirect("jobs:home")

    ss = get_object_or_404(SavedCandidateSearch, id=search_id, recruiter=request.user)
    qs = _apply_candidate_filters(ss.filters)

    return render(request, "applications/run_saved_search.html", {
        "search": ss,
        "candidates": qs,
    })


@login_required
def delete_saved_search(request, search_id):
    if not request.user.is_recruiter:
        return redirect("jobs:home")

    ss = get_object_or_404(SavedCandidateSearch, id=search_id, recruiter=request.user)
    ss.delete()
    return redirect("applications:saved_searches")


@login_required
def notifications(request):
    if not request.user.is_recruiter:
        return redirect("jobs:home")

    _refresh_saved_search_notifications(request.user)

    notes = RecruiterNotification.objects.filter(user=request.user).order_by("-created_at")

    if request.method == "POST":
        RecruiterNotification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return redirect("applications:notifications")

    return render(request, "applications/notifications.html", {"notifications": notes})