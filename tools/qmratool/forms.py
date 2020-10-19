from django import forms
from .models import RiskAssessment, SourceWater, Exposure, Treatment

class RAForm(forms.ModelForm):
    class Meta:
        model=RiskAssessment
        fields=["name","description","source","treatment", "exposure"]

        

class SourceWaterForm(forms.Form):
    sourcewater=forms.ModelChoiceField(queryset=SourceWater.objects.all(), to_field_name="sourcewater")
    description=forms.CharField(required=False)

class ExposureForm(forms.ModelForm):
    class Meta:
        model=Exposure
        fields=["use","description", "events_per_year", "volume_per_event"]


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields=["name", "group", "description"]

