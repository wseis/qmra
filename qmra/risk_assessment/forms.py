from django import forms
from django.forms import modelformset_factory, HiddenInput

from crispy_forms.bootstrap import AppendedText, Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Div, HTML, Button

from qmra.risk_assessment.models import Inflow, DefaultPathogens, DefaultTreatments, Treatment, \
    RiskAssessment


class RiskAssessmentForm(forms.ModelForm):
    class Meta:
        model = RiskAssessment
        fields = [
            "name",
            "description",
            "source_name",
            "exposure_name",
            "events_per_year",
            "volume_per_event"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source_name"].label = "Select a source type to add inflows"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.label_class = "text-muted small"
        self.helper.layout = Layout(
            Row(Column("name"), Column("description")),
            Row(Column("exposure_name"), Column("events_per_year"), Column("volume_per_event"), css_id="exposure-form-fieldset"),
            # Row("source_name", css_id="source-form")
        )


class InflowForm(forms.ModelForm):
    # DELETE = forms.BooleanField(label="remove")

    class Meta:
        model = Inflow
        fields = ['pathogen', 'min', 'max']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.render_hidden_fields = False
        self.helper.render_unmentioned_fields = False
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = "text-muted small"
        self.fields['pathogen'].choices = DefaultPathogens.choices()
        self.fields['pathogen'].label = "Pathogen"
        self.fields['min'].label = "Minimum concentration"
        self.fields['max'].label = "Maximum concentration"
        self.fields['max'].required = True
        self.helper.layout = Layout(
            Column('pathogen'),
            Column(AppendedText('min', 'N/L')),
            Column(AppendedText('max', 'N/L')),
            # "DELETE"
        )


InflowFormSetBase = modelformset_factory(
    Inflow, form=InflowForm,
    extra=0, max_num=30, min_num=0,
    can_delete=True, can_delete_extra=True
)


class InflowFormSet(InflowFormSetBase):
    def get_deletion_widget(self):
        return forms.CheckboxInput(attrs=dict(label="remove"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # for form in self.forms:
        #     form.fields["DELETE"].label = "remove"


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = [
            "name",
            "bacteria_min",
            "bacteria_max",
            'viruses_min',
            'viruses_max',
            "protozoa_min",
            "protozoa_max"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = "text-muted small"
        self.fields['name'].choices = DefaultTreatments.choices()
        self.fields['name'].label = ""
        self.fields['bacteria_min'].label = ""
        self.fields['bacteria_max'].label = ""
        self.fields['viruses_min'].label = ""
        self.fields['viruses_max'].label = ""
        self.fields['protozoa_min'].label = ""
        self.fields['protozoa_max'].label = ""
        label_style = "class='text-muted text-center w-100'"
        self.helper.layout = Layout(
            Field("name", css_class="disabled-input text-center"),
            Row(Column(HTML(f"<div></div>"), css_class="col-2"),
                Column(HTML(f"<label class='text-muted text-center w-100'>Minimum</label>")),
                Column(HTML(f"<label class='text-muted text-center w-100'>Maximum</label>")), css_class=""),
            Row(Column(HTML(f"<label {label_style}>Bacteria LRV:</label>"), css_class="align-content-center col-2"),
                Column("bacteria_min", css_class=""), Column("bacteria_max"), css_class="align-items-baseline"),
            Row(Column(HTML(f"<label {label_style}>Viruses LRV:</label>"), css_class="align-content-center col-2"),
                Column("viruses_min"), Column("viruses_max"), css_class="align-items-baseline"),
            Row(Column(HTML(f"<label {label_style}>Protozoa LRV:</label>"), css_class="align-content-center col-2"),
                Column("protozoa_min"), Column("protozoa_max"), css_class="align-items-baseline"),
            # Row(Column("DELETE"))
        )


TreatmentFormSetBase = modelformset_factory(
    Treatment, form=TreatmentForm,
    extra=0, max_num=30, min_num=0,
    can_delete=True, can_delete_extra=True
)


class AddTreatmentForm(forms.Form):
    select_treatment = forms.ChoiceField(choices=DefaultTreatments.choices(), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["select_treatment"].required = False
        self.fields["select_treatment"].label = "Select treatment to add"
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = "text-muted"
        self.helper.layout = Layout(
            "select_treatment",
        )


class TreatmentFormSet(TreatmentFormSetBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        if not kwargs.get("queryset", False):
            self.queryset = Treatment.objects.none()
