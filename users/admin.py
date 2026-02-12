from django.contrib import admin
from .models import JobSeekerProfile, RecruiterProfile, User

# Register your models here.

admin.site.register(User)
admin.site.register(JobSeekerProfile)
admin.site.register(RecruiterProfile)


