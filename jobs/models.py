from django.db import models
from django.conf import settings

# Create your models here.
# Implement User Story models here.

class JobPosting(models.Model):
    """
    User Story 10: Recruiters post and edit job roles.
    """
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_posts')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

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

    def __str__(self):
        return self.title
