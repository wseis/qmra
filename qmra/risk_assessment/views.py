from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from qmra.risk_assessment.forms import InflowFormSet, RiskAssessmentForm, TreatmentFormSet, AddTreatmentForm
from qmra.risk_assessment.models import Inflow, RiskAssessment, Treatment
from qmra.risk_assessment.plots import risk_plots, inflows_plot, treatments_plot
from qmra.risk_assessment.risk import assess_risk
from django.db import transaction


@transaction.atomic
def create_risk_assessment(user, risk_assessment_form, inflow_form, treatment_form):
    risk_assessment = risk_assessment_form.save(commit=False)
    risk_assessment.user = user
    risk_assessment.save()
    inflows = inflow_form.save(commit=False)
    for deleted in inflow_form.deleted_forms:
        deleted.instance.delete()
    for inflow in inflows:
        inflow.risk_assessment = risk_assessment
        inflow.save()
    treatments = treatment_form.save(commit=False)
    for deleted in treatment_form.deleted_forms:
        deleted.instance.delete()
    for treatment in treatments:
        treatment.risk_assessment = risk_assessment
        treatment.save()
    # print(risk_assessment.inflows.values("pathogen").all(), risk_assessment.treatments.values("name").all())
    return risk_assessment


@transaction.atomic
def assess_and_save_results(risk_assessment: RiskAssessment) -> RiskAssessment:
    results = assess_risk(risk_assessment, risk_assessment.inflows.all(),
                          risk_assessment.treatments.all())
    for r in results.values():
        r.save()
    return RiskAssessment.objects.get(id=risk_assessment.id)


@login_required(login_url="/login")
def list_risk_assessment_view(request):
    return render(request, "risk-assessment-list.html",
                  context=dict(assessments=request.user.risk_assessments.order_by("-created_at").all()))


@login_required(login_url="/login")
def risk_assessment_view(request, risk_assessment_id=None):
    if request.method == "POST":
        if risk_assessment_id is not None:
            instance = RiskAssessment.objects.get(id=risk_assessment_id)
            inflows = instance.inflows.all()
            treatments = instance.treatments.all()
        else:
            instance = None
            inflows = Inflow.objects.none()
            treatments = Treatment.objects.none()
        risk_assessment_form = RiskAssessmentForm(request.POST, instance=instance, prefix="ra")
        inflow_form = InflowFormSet(request.POST, queryset=inflows, prefix="inflow")
        treatment_form = TreatmentFormSet(request.POST, queryset=treatments, prefix="treatments")
        if risk_assessment_form.is_valid() and \
                inflow_form.is_valid() and \
                treatment_form.is_valid():
            ra = create_risk_assessment(request.user, risk_assessment_form, inflow_form, treatment_form)
            for r in ra.results.all():
                r.delete()
            ra = assess_and_save_results(ra)
            return HttpResponseRedirect(reverse("assessment", kwargs=dict(risk_assessment_id=ra.id)))
        else:
            print(inflow_form.errors)
            print(treatment_form.errors)
            return render(request, "assessment-configurator.html",
                          context=dict(
                              risk_assessment_form=risk_assessment_form,
                              inflow_form=inflow_form,
                              add_treatment_form=AddTreatmentForm(),
                              treatment_form=treatment_form
                          ))
    if risk_assessment_id is None:
        return render(request, "assessment-configurator.html",
                      context=dict(
                          risk_assessment_form=RiskAssessmentForm(
                              prefix="ra", initial=dict(name=f"Assessment {len(request.user.risk_assessments.all())+1}")),
                          inflow_form=InflowFormSet(queryset=Inflow.objects.none(), prefix="inflow"),
                          add_treatment_form=AddTreatmentForm(),
                          treatment_form=TreatmentFormSet(prefix="treatments")
                      ))
    risk_assessment = RiskAssessment.objects.get(id=risk_assessment_id)
    if request.method == "DELETE":
        risk_assessment.delete()
        return render(request, "risk-assessment-list.html",
                      context=dict(assessments=request.user.risk_assessments.all()))

    return render(request, "assessment-configurator.html",
                  context=dict(
                      risk_assessment=risk_assessment,
                      risk_assessment_form=RiskAssessmentForm(instance=risk_assessment, prefix="ra"),
                      inflow_form=InflowFormSet(queryset=risk_assessment.inflows.all(), prefix="inflow"),
                      add_treatment_form=AddTreatmentForm(),
                      treatment_form=TreatmentFormSet(queryset=risk_assessment.treatments.all(), prefix="treatments")
                  ))


@login_required(login_url="/login")
def risk_assessment_result(request):
    if request.method == "POST":
        risk_assessment_form = RiskAssessmentForm(request.POST, instance=None, prefix="ra")
        inflow_form = InflowFormSet(request.POST, queryset=Inflow.objects.none(), prefix="inflow")
        treatment_form = TreatmentFormSet(request.POST, queryset=Treatment.objects.none(), prefix="treatments")
        if risk_assessment_form.is_valid() and \
                inflow_form.is_valid() and \
                treatment_form.is_valid():
            ra = risk_assessment_form.save(commit=False)
            # print(inflow_form.is_valid(), treatment_form.is_valid())
            inflows = inflow_form.save(commit=False)
            for deleted in inflow_form.deleted_forms:
                deleted.instance.delete()
            treatments = treatment_form.save(commit=False)
            for deleted in treatment_form.deleted_forms:
                deleted.instance.delete()
            results = assess_risk(ra,
                                  inflows,
                                  treatments, save=False)
            plots = risk_plots(results.values())
            return render(request, "assessment-result.html",
                          context=dict(results=results.values(),
                                       infection_risk=any(r.infection_risk for r in results.values()),
                                       dalys_risk=any(r.dalys_risk for r in results.values()),
                                       risk_plot=plots[0], daly_plot=plots[1]))
        else:
            print(inflow_form.errors)
            print(treatment_form.errors)
            return HttpResponse(status=422)

    elif request.method == "GET":
        risk_assessment_id = request.GET.get("id")
        if risk_assessment_id is not None:
            risk_assessment = RiskAssessment.objects.get(id=risk_assessment_id)
            if not any(risk_assessment.results.all()):
                risk_assessment = assess_and_save_results(risk_assessment)
            results = risk_assessment.results.all()
            plots = risk_plots(results)
            return render(request, "assessment-result.html",
                          context=dict(results=results,
                                       infection_risk=risk_assessment.infection_risk,
                                       dalys_risk=risk_assessment.dalys_risk,
                                       risk_plot=plots[0], daly_plot=plots[1]))


@login_required(login_url="/login")
def inflows_plots_view(request):
    forms = InflowFormSet(request.POST, queryset=Inflow.objects.none(), prefix="inflow")
    forms.is_valid()
    print(forms.errors)
    inflows = forms.save(commit=False)
    for f in forms.deleted_forms:
        f.instance.delete()
    plot = inflows_plot(inflows)
    return render(request, "inflows-plot.html",
                  context=dict(plot=plot))


@login_required(login_url="/login")
def treatments_plots_view(request):
    forms = TreatmentFormSet(request.POST, prefix="treatments")
    forms.is_valid()
    print(forms.errors)
    treatments = forms.save(commit=False)
    for f in forms.deleted_forms:
        f.instance.delete()
    plot = treatments_plot(treatments)
    return render(request, "treatments-plot.html",
                  context=dict(plot=plot))
