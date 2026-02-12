from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, JobSeekerProfile, RecruiterProfile

@receiver(post_save, sender=User)
def create_profiles(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.is_job_seeker:
        JobSeekerProfile.objects.get_or_create(user=instance)
    if instance.is_recruiter:
        RecruiterProfile.objects.get_or_create(user=instance, defaults={"company_name": ""})