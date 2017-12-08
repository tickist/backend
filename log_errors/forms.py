from django import forms
from .models import LogError


class LogErrorForm(forms.ModelForm):

    class Meta:
        model = LogError
        fields = ["user", "location", "stack", "message"]