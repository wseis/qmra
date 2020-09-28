from django.forms import ModelForm
from .models import RiskAssessment

class RAForm(ModelForm):
    class Meta:
        model=RiskAssessment
        fields=["name", "description"]