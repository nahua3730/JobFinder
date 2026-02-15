
# Create your models here.
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
