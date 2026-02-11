from django import forms
from .models import JobSeekerProfile

class JobSeekerProfileForm(forms.ModelForm):
    # the base edit profile form
    class Meta:
        model = JobSeekerProfile
        fields = ["headline", "skills", "education", "work_experience", "links"]