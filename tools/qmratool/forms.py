from django import forms
from .models import (
    User,
    RiskAssessment,
    SourceWater,
    Inflow,
    PathogenGroup,
    Exposure,
    Treatment,
    LogRemoval,
    Reference,
    Comparison,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, Div
from formtools.wizard.views import SessionWizardView
from django.forms import modelformset_factory

class RAForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(RAForm, self).__init__(*args, **kwargs)
        self.fields[
            "treatment"
        ].help_text = "Please select your treatment configuration"
        self.fields["source"].help_text = "Please select your source water"
        self.fields["source"].empty_label = None
        self.fields["exposure"].empty_label = None
        self.fields["exposure"].help_text = "Please define your exposure scenario"
        self.fields["exposure"].queryset = Exposure.objects.filter(
            user__in=[user, 1]
        ).order_by("id")
        self.fields["treatment"].queryset = (
            Treatment.objects.filter(user__in=[user, 1])
            .order_by("id")
            .order_by("category")
        )
        self.fields["name"].widget.attrs.update({'class': 'text-field-bg'})
        self.fields["description"].widget.attrs.update({'class': 'text-field-bg'})
        
        self.helper = FormHelper()
        
        self.helper.layout = Layout(
            Div('source', css_class='radio-div-bg'),
            Div('exposure', css_class='radio-div-bg'),
            # Add other fields or layout objects as nee
        )
        

    class Meta:
        model = RiskAssessment
        fields = ["name", "description", "source", "treatment", "exposure"]
        widgets = {
            "source": forms.RadioSelect(attrs={"class": "radio-bg", "empty_label": None}),
            "treatment": forms.CheckboxSelectMultiple(attrs={"class": "checkbox-bg"}),
            "exposure": forms.RadioSelect(attrs={"class": "radio-bg", "empty_label": None}),
        }
     


class SourceWaterForm(forms.ModelForm):
    class Meta:
        model = SourceWater
        fields = ["water_source_name", "water_source_description"]


class InflowForm(forms.ModelForm):
    class Meta:
        model = Inflow
        fields = ['pathogen', 'min', 'max']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['pathogen'].disabled = True
        self.helper.layout = Layout(
            'pathogen',
            'min',
            'max',
            # Add more fields as needed
        )
InflowFormSet = modelformset_factory(Inflow, form=InflowForm, extra=3)

class ExposureForm(forms.ModelForm):
    class Meta:
        model = Exposure
        fields = [
            "name",
            "description",
            "events_per_year",
            "volume_per_event",
            "reference",
        ]

    def __init__(self, *args, **kwargs):
        super(ExposureForm, self).__init__(*args, **kwargs)
        self.fields[
            "name"
        ].help_text = "The name of the exposure scenario should be unique"
        self.fields[
            "description"
        ].help_text = "Please enter  a short description of the exposure scenario"

        self.fields[
            "events_per_year"
        ].help_text = "Please enter the number of expected exposure events per year"
        self.fields[
            "volume_per_event"
        ].help_text = (
            "Please enter the volume per exposure event in liters (e.g. 50 mL = 0.050)"
        )
        self.fields["reference"].queryset = Reference.objects.filter(id=51)


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ["name", "description"]


class LogRemovalForm(forms.ModelForm):
    class Meta:
        model = LogRemoval
        fields = ["pathogen_group", "reference","min", "max"]

    def __init__(self, *args, **kwargs):
        super(LogRemovalForm, self).__init__(*args, **kwargs)
        self.fields["reference"].queryset = Reference.objects.filter(id=51)
        self.fields['reference'].disabled = True
        self.fields['pathogen_group'].disabled = True
        #self.fields["pathogen_group"].widget = forms.HiddenInput()

LogRemovalFormSet = modelformset_factory(LogRemoval, form=LogRemovalForm, extra=3)


class ComparisonForm(forms.ModelForm):
    class Meta:
        model = Comparison
        fields = ["risk_assessment"]
        widgets = {"risk_assessment": forms.CheckboxSelectMultiple()}

    def __init__(self, user, *args, **kwargs):
        super(ComparisonForm, self).__init__(*args, **kwargs)
        self.fields["risk_assessment"].queryset = RiskAssessment.objects.filter(
            user=user
        )
        self.fields[
            "risk_assessment"
        ].help_text = "Select risk assessments for comparison"
        self.helper = FormHelper()


# Step 1
class RAFormStep1(forms.ModelForm):

    
    class Meta:
        model = RiskAssessment
        fields = ["name", "description"]

# Step 2
class RAFormStep2(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RAFormStep2, self).__init__(*args, **kwargs)
        self.fields["source"].help_text = "Please select your source water"
        self.fields["source"].empty_label = None
        self.helper = FormHelper()
    class Meta:
        model = RiskAssessment
        fields = ["source"]
        widgets = {
            "source": forms.RadioSelect(attrs={"empty_label": None}),
        }

# Step 3
class RAFormStep3(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        super(RAFormStep3, self).__init__(*args, **kwargs)
        self.fields[
            "treatment"
        ].help_text = "Please select your treatment configuration"
        
        self.fields["treatment"].queryset = (
            Treatment.objects.filter(user__in=[1])
            .order_by("id")
            .order_by("category")
        )
        self.helper = FormHelper()
    class Meta:
        model = RiskAssessment
        fields = ["treatment"]
        widgets = {
            "treatment": forms.CheckboxSelectMultiple(),
        }

# Step 4
class RAFormStep4(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RAFormStep4, self).__init__(*args, **kwargs)
   
        self.fields["exposure"].empty_label = None
        self.fields["exposure"].help_text = "Please define your exposure scenario"
        self.fields["exposure"].queryset = Exposure.objects.filter(
            user__in=[ 1]
        ).order_by("id")
     
        self.helper = FormHelper()
    class Meta:
        model = RiskAssessment
        fields = ["exposure"]
        widgets = {
            "exposure": forms.RadioSelect(attrs={"empty_label": None}),
        }




#     def __init__(self, user, *args, **kwargs):
#         super(RAForm, self).__init__(*args, **kwargs)
#         self.fields[
#             "treatment"
#         ].help_text = "Please select your treatment configuration"
#         self.fields["source"].help_text = "Please select your source water"
#         self.fields["source"].empty_label = None
#         self.fields["exposure"].empty_label = None
#         self.fields["exposure"].help_text = "Please define your exposure scenario"
#         self.fields["exposure"].queryset = Exposure.objects.filter(
#             user__in=[user, 1]
#         ).order_by("id")
#         self.fields["treatment"].queryset = (
#             Treatment.objects.filter(user__in=[user, 1])
#             .order_by("id")
#             .order_by("category")
#         )
#         self.helper = FormHelper()

#     class Meta:
#         model = RiskAssessment
#         fields = ["name", "description", "source", "treatment", "exposure"]
#         widgets = {
#             "source": forms.RadioSelect(attrs={"empty_label": None}),
#             "treatment": forms.CheckboxSelectMultiple(),
#             "exposure": forms.RadioSelect(attrs={"empty_label": None}),
#         }
# '