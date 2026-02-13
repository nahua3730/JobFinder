from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, JobSeekerProfile, RecruiterProfile
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role Information", {
            "fields": ("is_job_seeker", "is_recruiter"),
        }),
    )

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_job_seeker",
        "is_recruiter",
        "is_staff",
    )
# Register your models here.
admin.site.register(JobSeekerProfile)
admin.site.register(RecruiterProfile)
