from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import JobPosting
User = get_user_model()

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "recruiter", "location", "is_remote", "created_at")
    search_fields = ("title", "description", "location", "skills", "recruiter__username")
    list_filter = ("is_remote", "created_at")
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "recruiter":
            kwargs["queryset"] = User.objects.filter(is_recruiter=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)