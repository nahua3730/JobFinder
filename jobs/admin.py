import csv
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from .models import JobPosting
User = get_user_model()

@admin.action(description="Export selected jobs to CSV")
def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_export.csv"'
    writer = csv.writer(response)

    field_names = [
        'id', 'title', 'recruiter', 'location', 'status',
        'min_salary', 'max_salary', 'is_remote', 
        'visa_sponsorship', 'created_at'
    ]
    writer.writerow(field_names)
    for obj in queryset:
        row = [str(getattr(obj, field)) for field in field_names]
        writer.writerow(row)
    return response

@admin.action(description="Approve selected jobs")
def approve_jobs(modeladmin, request, queryset):
    queryset.update(status=JobPosting.Status.APPROVED)

@admin.action(description="Mark selected jobs as Spam")
def mark_as_spam(modeladmin, request, queryset):
    queryset.update(status=JobPosting.Status.SPAM)

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "recruiter", "location", "status", "is_remote", "created_at")
    
    search_fields = ("title", "description", "location", "street_address", "city", "state", "zip_code", "skills", "recruiter__username")
    
    list_filter = ("status", "is_remote", "created_at", "visa_sponsorship", "state")
    
    actions = [export_as_csv, approve_jobs, mark_as_spam]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "recruiter":
            kwargs["queryset"] = User.objects.filter(is_recruiter=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)