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
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit


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
        self.helper = FormHelper()

    class Meta:
        model = RiskAssessment
        fields = ["name", "description", "source", "treatment", "exposure"]
        widgets = {
            "source": forms.RadioSelect(attrs={"empty_label": None}),
            "treatment": forms.CheckboxSelectMultiple(),
            "exposure": forms.RadioSelect(attrs={"empty_label": None}),
        }


class SourceWaterForm(forms.ModelForm):
    class Meta:
        model = SourceWater
        fields = ["water_source_name", "water_source_description"]


class InflowForm(forms.ModelForm):
    class Meta:
        model = Inflow
        fields = ["pathogen", "min", "max", "reference"]


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
        fields = ["min", "max", "pathogen_group", "reference"]

    def __init__(self, *args, **kwargs):
        super(LogRemovalForm, self).__init__(*args, **kwargs)
        self.fields["reference"].queryset = Reference.objects.filter(id=51)
        self.fields["pathogen_group"].widget = forms.HiddenInput()


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
