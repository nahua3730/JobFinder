from django import forms
from .models import JobPosting

VISA_CHOICES = [
    ("", "Any"),
    ("true", "Yes"),
    ("false", "No"),
]

REMOTE_CHOICES = [
    ("", "Any"),
    ("true", "Remote"),
    ("false", "On-site"),
]


class JobSearchForm(forms.Form):
    title = forms.CharField(required=False)
    skills = forms.CharField(required=False, help_text="Comma-separated (e.g., Python, SQL)")
    location = forms.CharField(required=False)

    salary_min = forms.IntegerField(required=False, min_value=0)
    salary_max = forms.IntegerField(required=False, min_value=0)

    is_remote = forms.ChoiceField(required=False, choices=REMOTE_CHOICES)
    visa_sponsorship = forms.ChoiceField(required=False, choices=VISA_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        self.fields["is_remote"].widget.attrs["class"] = "form-select"
        self.fields["visa_sponsorship"].widget.attrs["class"] = "form-select"

# User Story 10
class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'location', 'salary_range', 'is_remote', 'visa_sponsorship']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control'}),
        }

# User story 11
class CandidateSearchForm(forms.Form):
    query = forms.CharField(required=False, label="Name or Skills", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, John Doe...'}))
    
    location = forms.CharField(required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Atlanta, GA'}))
    
    has_projects = forms.BooleanField(required=False, label="Must have Projects listed",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))