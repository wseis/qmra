from django import forms
from .models import RiskAssessment, SourceWater,Inflow,  Exposure, Treatment, LogRemoval
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit

class RAForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(RAForm, self).__init__(*args, **kwargs)
        self.fields['treatment'].help_text = "Please select your treatment configuration"
        self.fields['source'].help_text = "Please select your source water"
        self.fields['exposure'].help_text = "Please define your exposure scenario"
        self.helper = FormHelper(self)
        self.fields['exposure'].queryset = Exposure.objects.filter(user__in=[user, 8])
        #self.fields['treatment'].queryset = Treatment.objects.filter(user__in=[user, 8])
        # uncommetn when User is added to treatment      
        
    class Meta:
        model=RiskAssessment
        fields=["name","description","source","treatment", "exposure"]
        widgets={"source": forms.RadioSelect(attrs={"empty_label":None}),
            "treatment": forms.CheckboxSelectMultiple()}
    
        
        

class RAForm2(forms.Form):
    treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(), to_field_name="name")
    

class SourceWaterForm(forms.ModelForm):
    class Meta():
        model = SourceWater
        fields = ["water_source_name", "water_source_description"]
        
    
class InflowForm(forms.ModelForm):
    class Meta():
        model = Inflow
        fields = ["pathogen", "min", "max", "reference"]


class ExposureForm(forms.ModelForm):
    class Meta:
        model=Exposure
        fields=["name","description", "events_per_year", "volume_per_event", "reference"]
    
class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields=["name", "description", "group"]


class LogRemovalForm(forms.ModelForm):
    class Meta:
        model = LogRemoval
        fields = ['min', 'max', 'pathogen_group', "reference"]
  
    #Treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(),  to_field_name="name")
    #treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(), to_field_name="group"