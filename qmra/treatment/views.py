from django import forms
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from qmra.treatment.models import Treatment, PathogenGroup, LogRemoval, Reference


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ["name", "description"]


class LogRemovalForm(forms.ModelForm):
    class Meta:
        model = LogRemoval
        fields = ["pathogen_group", "min", "max"]

    def __init__(self, *args, **kwargs):
        super(LogRemovalForm, self).__init__(*args, **kwargs)
        self.fields['pathogen_group'].disabled = True
        self.fields['min'].label = "Minimum Logremoval"
        self.fields['max'].label = "Maximum Logremoval"


LogRemovalFormSetBase = modelformset_factory(
    LogRemoval,
    form=LogRemovalForm, extra=3,
    min_num=3, max_num=3
)


class LogRemovalFormSet(LogRemovalFormSetBase):
    def __init__(self, *args, **kwargs):
        kwargs["initial"] = kwargs.get(
            "initial",
            [
                dict(pathogen_group=PathogenGroup.objects.filter(
                    pathogen_group="Viruses").first().id),
                dict(pathogen_group=PathogenGroup.objects.filter(
                    pathogen_group="Bacteria").first().id),
                dict(pathogen_group=PathogenGroup.objects.filter(
                    pathogen_group="Protozoa").first().id)
            ])
        super().__init__(*args, **kwargs)


def create_treatment_and_logremoval(
        user,
        treatment_form,
        logremoval_formset: LogRemovalFormSetBase
):
    created_treatment = treatment_form.save(commit=False)
    created_treatment.user = user
    created_treatment.save()

    logremoval_instances = logremoval_formset.save(commit=False)
    for logremoval in logremoval_instances:
        logremoval.treatment = created_treatment
        logremoval.save()


@login_required(login_url="/login")
def treatment_view(request, treatment_id=None):
    if treatment_id is None:
        if request.method == "POST":
            treatment_form = TreatmentForm(data=request.POST)
            logremoval_formset = LogRemovalFormSet(request.POST)
            if treatment_form.is_valid() and logremoval_formset.is_valid():
                create_treatment_and_logremoval(request.user, treatment_form, logremoval_formset)
                return HttpResponseRedirect(reverse("treatment"))
            else:
                return render(request, "treatment-form.html",
                              {
                                  "treatment_form": treatment_form,
                                  "logremoval_formset": logremoval_formset
                              })
        else:
            if request.GET.get("form"):
                return render(request, "treatment-form.html",
                              {
                                  "treatment_form": TreatmentForm(),
                                  "logremoval_formset": LogRemovalFormSet(queryset=LogRemoval.objects.none())})
            return render(request, "treatment.html",
                          {
                              "treatments": request.user.treatments.all()
                          })
    if request.method == "GET":
        treatment = Treatment.objects.get(id=treatment_id)
        if request.GET.get("form"):
            return render(request, "treatment-form.html",
                          {
                              "treatment_form": TreatmentForm(instance=treatment),
                              "logremoval_formset": LogRemovalFormSet(queryset=treatment.logremoval.all())})
        return JsonResponse([treatment.serialize()], safe=False)
    elif request.method == "POST":
        treatment = Treatment.objects.get(id=treatment_id)
        treatment_form = TreatmentForm(instance=treatment, data=request.POST)
        logremoval_formset = LogRemovalFormSet(request.POST, queryset=treatment.logremoval.all())
        if treatment_form.is_valid() and logremoval_formset.is_valid():
            create_treatment_and_logremoval(request.user, treatment_form, logremoval_formset)
            return HttpResponseRedirect(reverse("treatment"))
        else:
            return render(request, "treatment-form.html",
                              {
                                  "treatment_form": treatment_form,
                                  "logremoval_formset": logremoval_formset
                              })
    elif request.method == "DELETE":  # shortcut because HTML form only supports GET & POST...
        Treatment.objects.get(id=treatment_id).delete()
        return HttpResponseRedirect(reverse("treatment"))
