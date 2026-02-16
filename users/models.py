from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_job_seeker = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)


class JobSeekerProfile(models.Model):
    """
    User Story 1: Profile with headline, skills, etc.
    User Story 5: Privacy options
    User Story 11: Candidate Search
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seeker_profile')
    headline = models.CharField(max_length=255, blank=True)
    skills = models.TextField(help_text="Comma-separated skills", blank=True)

    education = models.TextField(blank=True)
    work_experience = models.TextField(blank=True)
    links = models.TextField(blank=True, help_text="Comma-separated URLs")

    privacy_enabled = models.BooleanField(default=False, help_text="Hide profile from recruiters")

    location = models.CharField(max_length=255, blank=True, help_text="City, State")
    street_address = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=2, blank=True, default="")
    zip_code = models.CharField(max_length=10, blank=True, default="")
    
    preferred_commute_radius_miles = models.PositiveIntegerField(default=10, help_text="Preferred commute radius in miles")

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    projects = models.TextField(blank=True, help_text="List of projects for search")

    show_headline = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_skills = models.BooleanField(default=True)
    show_education = models.BooleanField(default=True)
    show_work_experience = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_links = models.BooleanField(default=True)

    def build_location_display(self) -> str:
        city = (self.city or "").strip()
        state = (self.state or "").strip().upper()
        zip_code = (self.zip_code or "").strip()

        if city and state:
            return f"{city}, {state} {zip_code}".strip()
        if city:
            return city
        if state:
            return state
        return zip_code

    def build_geocode_query(self) -> str:
        parts = []
        if (self.street_address or "").strip():
            parts.append(self.street_address.strip())

        display = self.build_location_display()
        if display:
            parts.append(display)

        q = ", ".join(parts)
        return f"{q}, USA" if q else ""

    def save(self, *args, **kwargs):
        self.location = self.build_location_display()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class RecruiterProfile(models.Model):
    """
    User Story 10: Link jobs to a company/recruiter.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=255)
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. Technical Recruiter, Hiring Manager"
    )
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name}"
