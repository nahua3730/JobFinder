from django.db import models
from django.conf import settings

# Create your models here.
# Implement User Story models here.

class JobPosting(models.Model):
    """
    User Story 10: Recruiters post and edit job roles.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        SPAM = 'SPAM', 'Spam / Rejected'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPROVED,
        help_text="Moderation status of the job posting"
    )

    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_posts')
    title = models.CharField(max_length=255)
    description = models.TextField()

    location = models.CharField(max_length=255, blank=True, default="")

    street_address = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=2, blank=True, default="")   # e.g. GA
    zip_code = models.CharField(max_length=10, blank=True, default="")  # 30332 or 30332-1234

    # Filtering fields (User Story 2)
    salary_range = models.CharField(max_length=100)

    #real salary numbers so you can filter properly
    min_salary = models.IntegerField(null=True, blank=True)
    max_salary = models.IntegerField(null=True, blank=True)

    # skills filter (comma-separated)
    skills = models.CharField(max_length=255, blank=True, default="", help_text="Comma-separated skills (e.g. Python, Java)")

    # existing remote flag
    is_remote = models.BooleanField(default=False)

    # visa sponsorship filter
    visa_sponsorship = models.BooleanField(default=False)

    # Map fields (User Story: 7, 8, 9)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def build_location_string(self) -> str:
        if self.is_remote:
            return "Remote"

        parts = []
        if self.street_address.strip():
            parts.append(self.street_address.strip())

        city_state = ""
        if self.city.strip() and self.state.strip():
            city_state = f"{self.city.strip()}, {self.state.strip().upper()}"
        elif self.city.strip():
            city_state = self.city.strip()
        elif self.state.strip():
            city_state = self.state.strip().upper()

        if city_state:
            if self.zip_code.strip():
                parts.append(f"{city_state} {self.zip_code.strip()}")
            else:
                parts.append(city_state)
        else:
            if self.zip_code.strip():
                parts.append(self.zip_code.strip())

        return ", ".join(parts) if parts else ""

    def save(self, *args, **kwargs):
        self.location = self.build_location_string()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
