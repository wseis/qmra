from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from qmra.treatment.models import Pathogen
from qmra.source.models import WaterSource, Inflow


def create_water_source_and_inflows(user, source_form, inflow_formset):
    created_water_source = source_form.save(commit=False)
    created_water_source.user = user
    created_water_source.save()

    inflow_instances = inflow_formset.save(commit=False)
    for inflow in inflow_instances:
        inflow.water_source = created_water_source
        inflow.save()


class WaterSourceForm(forms.ModelForm):
    class Meta:
        model = WaterSource
        fields = ["name", "description"]


class InflowForm(forms.ModelForm):
    class Meta:
        model = Inflow
        fields = ['pathogen', 'min', 'max']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['pathogen'].disabled = True
        self.fields['min'].label = "Minimum concentration"
        self.fields['max'].label = "Maximum concentration"

        self.helper.layout = Layout(
            'pathogen',
            'min',
            'max',
        )


InflowFormSetBase = modelformset_factory(
    Inflow, form=InflowForm,
    extra=3, max_num=3, min_num=3
)


class InflowFormSet(InflowFormSetBase):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = kwargs.get("initial", [
            dict(pathogen=Pathogen.objects.get(name="Rotavirus")),
            dict(pathogen=Pathogen.objects.get(name="Campylobacter jejuni")),
            dict(pathogen=Pathogen.objects.get(name="Cryptosporidium parvum"))
        ])
        super().__init__(*args, **kwargs)


@login_required()
def source_view(request, source_id=None):
    if source_id is None:
        if request.method == "POST":
            source_form = WaterSourceForm(data=request.POST)
            inflow_formset = InflowFormSet(request.POST)
            if source_form.is_valid() and inflow_formset.is_valid():
                create_water_source_and_inflows(request.user, source_form, inflow_formset)
                return HttpResponseRedirect(reverse("source"))
            else:
                return render(request, "source-form.html",
                              {
                                  "source_form": source_form,
                                  "inflow_formset": inflow_formset
                              })
        else:
            if request.GET.get("form"):
                return render(request, "source-form.html",
                       {
                           "source_form": WaterSourceForm(),
                           "inflow_formset": InflowFormSet(queryset=Inflow.objects.none())
                       })
            return render(request, "source.html",
                          {
                              "sources": request.user.water_sources.all(),
                          })
    if request.method == "GET":
        source = WaterSource.objects.get(id=source_id)
        if request.GET.get("form"):
            return render(request, "source-form.html",
                          {
                              "source_form": WaterSourceForm(instance=source),
                              "inflow_formset": InflowFormSet(queryset=source.inflow.all())
                          }
                          )
        return JsonResponse([source.serialize()], safe=False)
    elif request.method == "POST":
        source = WaterSource.objects.get(id=source_id)
        source_form = WaterSourceForm(instance=source, data=request.POST)
        inflow_formset = InflowFormSet(request.POST, queryset=source.inflow.all())
        if source_form.is_valid() and inflow_formset.is_valid():
            create_water_source_and_inflows(request.user, source_form, inflow_formset)
            return HttpResponseRedirect(reverse("source"))
        else:
            return render(request, "source-form.html",
                          {
                              "source_form": source_form,
                              "inflow_formset": inflow_formset
                          })
    elif request.method == "DELETE":
        WaterSource.objects.get(id=source_id).delete()
        return HttpResponseRedirect(reverse("source"))
