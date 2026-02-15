from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["note"]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 4, "placeholder": "Write a short tailored note (optional)..."})
        }

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"})
        }