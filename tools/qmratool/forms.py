from django import forms
from .models import RiskAssessment, SourceWater, Exposure, Treatment

class RAForm(forms.ModelForm):
    class Meta:
        model=RiskAssessment
        fields=["name","description","source","treatment", "exposure"]
        widgets={"source": forms.RadioSelect(attrs={"empty_label":None}),
            "treatment": forms.CheckboxSelectMultiple()}


class RAForm2(forms.Form):
    treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(), to_field_name="name")
    

class SourceWaterForm(forms.Form):
    sourcewater=forms.ModelMultipleChoiceField(queryset=SourceWater.objects.all(),  to_field_name="water_source_name")
    description=forms.CharField(required=False)

class ExposureForm(forms.ModelForm):
    class Meta:
        model=Exposure
        fields=["use","description", "events_per_year", "volume_per_event"]


class TreatmentForm(forms.Form):
    pass
    #Treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(),  to_field_name="name")
    #treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(), to_field_name="group"