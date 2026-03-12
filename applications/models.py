from django.conf import settings
from django.db import models

class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        REVIEW = "review", "Review"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        CLOSED = "closed", "Closed"

    job = models.ForeignKey("jobs.JobPosting", on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")

    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("job", "applicant") 
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.applicant} -> {self.job} ({self.status})"
    
class SavedCandidateSearch(models.Model):
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_candidate_searches"
    )
    name = models.CharField(max_length=255, blank=True, default="")
    filters = models.JSONField(default=dict)  # {"query": "...", "location": "...", "has_projects": true/false}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name or f"Saved Search #{self.id}"


class SavedSearchSeenCandidate(models.Model):
    saved_search = models.ForeignKey(SavedCandidateSearch, on_delete=models.CASCADE, related_name="seen")
    candidate_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("saved_search", "candidate_user")

    def __str__(self):
        return f"{self.saved_search_id} -> {self.candidate_user_id}"


class RecruiterNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recruiter_notifications")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default="")
    url = models.CharField(max_length=500, blank=True, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.title}"

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    
    message = models.CharField(max_length=255)
    
    link = models.CharField(max_length=255, blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"] 

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"
    
class Message(models.Model):
    class Delivery(models.TextChoices):
        IN_APP = "in_app", "In-app"
        EMAIL = "email", "Email"

    class EmailStatus(models.TextChoices):
        LOGGED = "logged", "Logged"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )

    job = models.ForeignKey(
        "jobs.JobPosting",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )

    subject = models.CharField(max_length=255, blank=True, default="")
    body = models.TextField()

    delivery = models.CharField(
        max_length=10,
        choices=Delivery.choices,
        default=Delivery.IN_APP,
    )

    is_read = models.BooleanField(default=False)

    to_email = models.EmailField(blank=True, default="")
    email_status = models.CharField(
        max_length=10,
        choices=EmailStatus.choices,
        default=EmailStatus.LOGGED,
    )
    error_message = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.delivery}: {self.sender} -> {self.recipient} ({self.created_at})"