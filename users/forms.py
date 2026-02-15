from django import forms
from .models import JobSeekerProfile, User, RecruiterProfile
from django.contrib.auth.forms import UserCreationForm


class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ["headline", "skills", "education", "work_experience", "projects", "links"]
        widgets = {
            "headline": forms.TextInput(attrs={
                "placeholder": "e.g., CS student seeking Summer 2026 internship"
            }),
            "skills": forms.TextInput(attrs={
                "placeholder": "Python, Java, SQL, React"
            }),
            "education": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "School, degree, graduation year, relevant courses"
            }),
            "work_experience": forms.Textarea(attrs={
                "rows": 6,
                "placeholder": "Role — Company — Dates\n• Impact / project / results"
            }),
            "projects": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "List your key projects here. This helps recruiters understand your experience!"
            }),
            "links": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "LinkedIn, GitHub, portfolio links (one per line)"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing_classes + " form-control").strip()


class SignUpForm(UserCreationForm):
    is_recruiter = forms.BooleanField(
        required=False, 
        label="I am a Recruiter (Leave unchecked if you are a Job Seeker)"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email", "is_recruiter")

class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = [
            "privacy_enabled",
            "show_headline",
            "show_skills",
            "show_education",
            "show_work_experience",
            "show_links",
        ]
class RecruiterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ["company_name", "title"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        fields = ("username", "email", "is_recruiter")
