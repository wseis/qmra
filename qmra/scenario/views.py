from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from qmra.scenario.models import ExposureScenario


def create_exposure_scenario(user, exposure_form):
    exposure = exposure_form.save(commit=False)
    exposure.user = user
    exposure.save()


class ExposureForm(forms.ModelForm):
    class Meta:
        model = ExposureScenario
        fields = [
            "name",
            "description",
            "events_per_year",
            "volume_per_event"
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


@login_required(login_url="/login")
def exposure_scenario_view(request, scenario_id = None):
    if scenario_id is None:
        if request.method == "POST":
            exposure_form = ExposureForm(data=request.POST)
            if exposure_form.is_valid():
                create_exposure_scenario(request.user, exposure_form)
                return HttpResponseRedirect(reverse("scenario"))
            else:
                return render(request, "scenario-form.html",
                       {
                           "scenario_form": exposure_form,
                       })
        else:
            if request.GET.get("form"):
                return render(request, "scenario-form.html",
                       {
                           "scenario_form": ExposureForm(),
                       })
            return render(request, "scenario.html",
                          {
                              "scenarios": request.user.scenarios.all(),
                          })
    if request.method == "GET":
        exposure = ExposureScenario.objects.get(id=scenario_id)
        if request.GET.get("form"):
            return render(request, "scenario-form.html",
                          {
                              "scenario_form": ExposureForm(instance=exposure),
                          })
        return JsonResponse([exposure.serialize()], safe=False)
    elif request.method == "POST":
        exposure = ExposureScenario.objects.get(id=scenario_id)
        exposure_form = ExposureForm(instance=exposure, data=request.POST)
        if exposure_form.is_valid():
            create_exposure_scenario(request.user, exposure_form)
            return HttpResponseRedirect(reverse("scenario"))
        else:
            return render(request, "scenario.html",
                          {
                              "scenarios": request.user.scenarios.all(),
                          })
    elif request.method == "DELETE":  # shortcut because HTML form only supports GET & POST...
        ExposureScenario.objects.get(id=scenario_id).delete()
        return HttpResponseRedirect(reverse("scenario"))

