from applications.models import Application, Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from types import SimpleNamespace
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail

from jobs.models import JobPosting
from users.models import JobSeekerProfile
from .models import (
    Application,
    SavedCandidateSearch,
    SavedSearchSeenCandidate,
    RecruiterNotification,
    Message,
)
from .forms import ApplicationForm, ApplicationStatusForm

User = get_user_model()

APPLICATION_STAGES = [
    {"value": Application.Status.APPLIED, "label": "Applied", "lane": "road", "badge_class": "status-applied"},
    {"value": Application.Status.REVIEW, "label": "Review", "lane": "grass", "badge_class": "status-review"},
    {"value": Application.Status.INTERVIEW, "label": "Interview", "lane": "river", "badge_class": "status-interview"},
    {"value": Application.Status.OFFER, "label": "Offer", "lane": "grass", "badge_class": "status-offer"},
    {"value": Application.Status.CLOSED, "label": "Closed", "lane": "road", "badge_class": "status-closed"},
]


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

            if not existing:
                Notification.objects.create(
                    recipient=job.recruiter,
                    message=f"New Applicant! {request.user.username} applied for {job.title}.",
                    link=reverse("jobs:job_applications", args=[job.id])
                )

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
    return render(request, "applications/my_applications.html", {
        "applications": apps,
        "application_stages": APPLICATION_STAGES,
    })


@login_required
def update_application_status(request, app_id):
    if getattr(request.user, "is_job_seeker", False):
        messages.error(request, "Only recruiters can move candidates through the pipeline.")
    return redirect("applications:my_applications")


@require_POST
@login_required
def update_application_status_api(request, app_id):
    return JsonResponse({"ok": False, "error": "forbidden"}, status=403)


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
            url = reverse("jobs:candidate_search") + "?" + _filters_to_querystring(ss.filters)

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

        if not (query or location or has_projects):
            messages.error(request, "Add at least one actual filter before saving a search.")
            return redirect("applications:saved_searches")

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
    items = []

    if getattr(request.user, "is_recruiter", False):
        _refresh_saved_search_notifications(request.user)
        recruiter_notes = RecruiterNotification.objects.filter(user=request.user)
        items.extend(
            SimpleNamespace(
                id=note.id,
                source="recruiter",
                title=note.title,
                body=note.body,
                url=note.url,
                is_read=note.is_read,
                created_at=note.created_at,
            )
            for note in recruiter_notes
        )

    legacy_notes = Notification.objects.filter(recipient=request.user)
    items.extend(
        SimpleNamespace(
            id=note.id,
            source="legacy",
            title="Notification",
            body=note.message,
            url=note.link or "",
            is_read=note.is_read,
            created_at=note.created_at,
        )
        for note in legacy_notes
    )

    items.sort(key=lambda note: note.created_at, reverse=True)
    return render(request, "applications/notifications.html", {"notifications": items})

@login_required
def mark_all_read(request):
    if request.method == "POST":
        request.user.notifications.filter(is_read=False).update(is_read=True)
        if getattr(request.user, "is_recruiter", False):
            RecruiterNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return redirect("applications:notifications")

@login_required
def read_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)

    if not notif.is_read:
        notif.is_read = True
        notif.save()

    return redirect(notif.link if notif.link else "applications:notifications")

@login_required
def delete_notification(request, notif_id):
    if request.method == "POST":
        notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
        notif.delete()

    return redirect("applications:notifications")


@login_required
def read_recruiter_notification(request, notif_id):
    notif = get_object_or_404(RecruiterNotification, id=notif_id, user=request.user)

    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=["is_read"])

    return redirect(notif.url or "applications:notifications")


@login_required
def delete_recruiter_notification(request, notif_id):
    if request.method == "POST":
        notif = get_object_or_404(RecruiterNotification, id=notif_id, user=request.user)
        notif.delete()

    return redirect("applications:notifications")

@login_required
def inbox(request):
    if not getattr(request.user, "is_job_seeker", False):
        return redirect("jobs:home")

    msgs = (
        Message.objects
        .filter(recipient=request.user, delivery=Message.Delivery.IN_APP)
        .select_related("sender", "job")
        .order_by("-created_at")
    )

    Message.objects.filter(recipient=request.user, delivery=Message.Delivery.IN_APP, is_read=False).update(is_read=True)

    return render(request, "applications/inbox.html", {"inbox_messages": msgs})

@login_required
def sent_messages(request):
    if not getattr(request.user, "is_recruiter", False):
        return redirect("jobs:home")

    msgs = (
        Message.objects
        .filter(sender=request.user)
        .select_related("recipient", "job")
        .order_by("-created_at")
    )
    return render(request, "applications/sent.html", {"sent_items": msgs})

@login_required
def compose_message(request, user_id):
    # Recruiter sends IN_APP message to a candidate
    if not getattr(request.user, "is_recruiter", False):
        return redirect("jobs:home")

    recipient = get_object_or_404(User, id=user_id)
    if not getattr(recipient, "is_job_seeker", False):
        messages.error(request, "You can only message job seekers.")
        return redirect("jobs:home")

    job = None
    job_id = request.GET.get("job_id")
    if job_id:
        job = JobPosting.objects.filter(id=job_id, recruiter=request.user).first()

    if request.method == "POST":
        subject = (request.POST.get("subject") or "").strip()
        body = (request.POST.get("body") or "").strip()

        if not body:
            messages.error(request, "Message body cannot be empty.")
            return redirect("applications:compose_message", user_id=recipient.id)

        msg = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            job=job,
            subject=subject,
            body=body,
            delivery=Message.Delivery.IN_APP,
        )

        Notification.objects.create(
            recipient=recipient,
            message=f"New message from recruiter {request.user.username}",
            link=reverse("applications:inbox")
        )

        messages.success(request, "Message sent!")
        return redirect("applications:sent_messages")

    return render(request, "applications/compose_message.html", {
        "recipient": recipient,
        "job": job,
    })


@login_required
def compose_email(request, user_id):
    if not getattr(request.user, "is_recruiter", False):
        return redirect("jobs:home")

    recipient = get_object_or_404(User, id=user_id)
    if not getattr(recipient, "is_job_seeker", False):
        messages.error(request, "You can only email job seekers.")
        return redirect("jobs:home")

    if not recipient.email:
        messages.error(request, "Candidate does not have an email on file.")
        return redirect("jobs:home")

    job = None
    job_id = request.GET.get("job_id")
    if job_id:
        job = JobPosting.objects.filter(id=job_id, recruiter=request.user).first()

    if request.method == "POST":
        subject = (request.POST.get("subject") or "").strip()
        body = (request.POST.get("body") or "").strip()

        if not subject:
            messages.error(request, "Email subject cannot be empty.")
            return redirect("applications:compose_email", user_id=recipient.id)
        if not body:
            messages.error(request, "Email body cannot be empty.")
            return redirect("applications:compose_email", user_id=recipient.id)

        msg = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            job=job,
            subject=subject,
            body=body,
            delivery=Message.Delivery.EMAIL,
            to_email=recipient.email,
            email_status=Message.EmailStatus.LOGGED,
        )

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            msg.email_status = Message.EmailStatus.SENT
            msg.save(update_fields=["email_status"])
            messages.success(request, f"Email sent to {recipient.email}!")
        except Exception as e:
            msg.email_status = Message.EmailStatus.FAILED
            msg.error_message = str(e)[:255]
            msg.save(update_fields=["email_status", "error_message"])
            messages.warning(request, "Email was logged, but sending failed (check email settings).")

        return redirect("applications:sent_messages")

    return render(request, "applications/compose_email.html", {
        "recipient": recipient,
        "job": job,
    })
