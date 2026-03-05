from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from users.models import JobSeekerProfile
from .models import SavedCandidateSearch, SavedSearchSeenCandidate, RecruiterNotification


def _apply_candidate_filters(filters):
    """
    Reuse your story 11 logic + enforce privacy.
    filters: dict with keys query/location/has_projects
    """
    query = (filters.get("query") or "").strip()
    location = (filters.get("location") or "").strip()
    has_projects = bool(filters.get("has_projects"))

    candidates = JobSeekerProfile.objects.filter(
        user__is_job_seeker=True,
        privacy_enabled=False,  # IMPORTANT: hide private profiles
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


def _refresh_saved_search_notifications(recruiter):
    """
    On-demand notification generation:
    - For each active saved search, re-run query
    - Find candidates not seen before
    - Create ONE notification with the count
    - Mark candidates as seen
    """
    saved_searches = SavedCandidateSearch.objects.filter(recruiter=recruiter, is_active=True)

    for ss in saved_searches:
        candidates_qs = _apply_candidate_filters(ss.filters).select_related("user")

        new_candidate_users = []
        for prof in candidates_qs:
            exists = SavedSearchSeenCandidate.objects.filter(
                saved_search=ss, candidate_user=prof.user
            ).exists()
            if not exists:
                new_candidate_users.append(prof.user)

        if new_candidate_users:
            # create notification
            count = len(new_candidate_users)
            title = f'New matches for "{ss.name or "Saved Search"}"'
            body = f"{count} new candidate(s) match your saved search."
            url = "/jobs/candidate-search/?" + _filters_to_querystring(ss.filters)

            RecruiterNotification.objects.create(
                user=recruiter,
                title=title,
                body=body,
                url=url,
            )

            # mark as seen
            SavedSearchSeenCandidate.objects.bulk_create(
                [SavedSearchSeenCandidate(saved_search=ss, candidate_user=u) for u in new_candidate_users],
                ignore_conflicts=True,
            )

        ss.last_checked_at = timezone.now()
        ss.save(update_fields=["last_checked_at"])


def _filters_to_querystring(filters):
    # minimal safe building (no imports needed)
    parts = []
    if filters.get("query"):
        parts.append(f'query={filters["query"]}')
    if filters.get("location"):
        parts.append(f'location={filters["location"]}')
    if filters.get("has_projects"):
        parts.append("has_projects=on")
    return "&".join(parts)


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

    # Generate notifications when recruiter visits saved searches (on-demand)
    _refresh_saved_search_notifications(request.user)

    searches = SavedCandidateSearch.objects.filter(recruiter=request.user).order_by("-created_at")
    return render(request, "applications/saved_searches.html", {"searches": searches})


@login_required
def run_saved_search(request, search_id):
    if not request.user.is_recruiter:
        return redirect("jobs:home")

    ss = get_object_or_404(SavedCandidateSearch, id=search_id, recruiter=request.user)
    qs = _apply_candidate_filters(ss.filters)

    return render(request, "applications/run_saved_search.html", {"search": ss, "candidates": qs})


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

    # refresh on open (on-demand)
    _refresh_saved_search_notifications(request.user)

    notes = RecruiterNotification.objects.filter(user=request.user).order_by("-created_at")

    if request.method == "POST":
        # mark all read
        RecruiterNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect("applications:notifications")

    return render(request, "applications/notifications.html", {"notifications": notes})