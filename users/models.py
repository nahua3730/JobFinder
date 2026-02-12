from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
#    Implement User Stories here.

#TEMP
class User(AbstractUser):
    """
    Custom user model to distinguish between Seekers and Recruiters.
    User Story 1 & 10
    """
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

    # added for story 1
    education = models.TextField(blank=True)
    work_experience = models.TextField(blank=True)
    links = models.TextField(blank=True, help_text="Comma-separated URLs")
    
    privacy_enabled = models.BooleanField(default=False, help_text="Hide profile from recruiters")
    
    # user story 11
    location = models.CharField(max_length=255, blank=True, help_text="City, State")
    projects = models.TextField(blank=True, help_text="List of projects for search")
    
    def __str__(self):
        return self.user.username
#END TEMP

class RecruiterProfile(models.Model):
    """
    User Story 10: Link jobs to a company/recruiter.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.company_name