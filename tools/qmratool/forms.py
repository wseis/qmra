from django import forms
from .models import RiskAssessment, SourceWater, Exposure, Treatment
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
    

class SourceWaterForm(forms.Form):
    sourcewater=forms.ModelMultipleChoiceField(queryset=SourceWater.objects.all(),  to_field_name="water_source_name")
    description=forms.CharField(required=False)

class ExposureForm(forms.ModelForm):
    class Meta:
        model=Exposure
        fields=["name","description", "events_per_year", "volume_per_event", "reference"]
    
#    def __init__(self, user, *args, **kwargs):
 #       super(ProductForm, self).__init__(*args, **kwargs)
  

class TreatmentForm(forms.Form):
    pass
    #Treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(),  to_field_name="name")
    #treatment=forms.ModelMultipleChoiceField(queryset=Treatment.objects.all(), to_field_name="group"