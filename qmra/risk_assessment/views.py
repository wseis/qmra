import numpy as np
import pandas as pd
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django_pandas.io import read_frame
from formtools.wizard.views import SessionWizardView
from plotly import express as px, graph_objs as go
from plotly.offline import plot

from qmra.source.models import Inflow
from qmra.risk_assessment.models import RiskAssessment, Health, DoseResponse, Comparison
from qmra.scenario.models import ExposureScenario
from qmra.treatment.models import Treatment, Pathogen, LogRemoval
from qmra.source.models import WaterSource


class RadioSelectWithTooltip(forms.RadioSelect):
    option_template_name = "option-with-tooltip.html"


class RAForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(RAForm, self).__init__(*args, **kwargs)
        self.fields[
            "treatment"
        ].help_text = "Please select your treatment configuration"
        self.fields["source"].help_text = "Please select your source water"
        self.fields["source"].empty_label = None
        self.fields["source"].queryset = WaterSource.objects.filter(
            Q(user__exact=user) | Q(user__isnull=True)
        ).order_by("id")
        self.fields["exposure"].empty_label = None
        self.fields["exposure"].help_text = "Please define your exposure scenario"
        self.fields["exposure"].queryset = ExposureScenario.objects.filter(
            Q(user__exact=user) | Q(user__isnull=True)
        ).order_by("id")
        self.fields["treatment"].queryset = (
            Treatment.objects.filter(
                Q(user__exact=user) | Q(user__isnull=True)
            )
            .order_by("id")
            .order_by("category")
        )

        self.fields["name"].widget.attrs.update({'class': 'text-field-bg'})
        self.fields["description"].widget.attrs.update({'class': 'text-field-bg'})

    class Meta:
        model = RiskAssessment
        fields = ["name", "description", "source", "treatment", "exposure"]
        widgets = {
            "source": forms.RadioSelect(attrs={"empty_label": None}),
            "treatment": forms.CheckboxSelectMultiple(),
            "exposure": forms.RadioSelect(attrs={"empty_label": None}),
        }


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


@login_required(login_url="/login")
def risk_assessment_view(request, risk_assessment_id=None):
    if risk_assessment_id is None:
        if request.method == "POST":
            ra_form = RAForm(request.user, request.POST)
            if ra_form.is_valid():
                ra = new_assessment(request.user, ra_form)
                return HttpResponseRedirect(reverse("assessment-result", kwargs=dict(risk_assessment_id=ra.id)))
            else:
                return HttpResponse(request, "Form not valid")
        else:
            if request.GET.get("form"):
                ra_form = RAForm(request.user)
                return render(request, "assessment-form.html",
                              {
                                  "ra_form": ra_form,
                                  "treatments": ra_form.fields["treatment"].queryset,
                                  "sources": ra_form.fields["source"].queryset,
                                  "exposures": ra_form.fields["exposure"].queryset
                              })
            return render(request, "assessment.html",
                          {"assessments": request.user.assessments.all()})
    elif request.method == "GET":
        ra = RiskAssessment.objects.get(id=risk_assessment_id)
        if request.GET.get("form", False):
            ra_form = RAForm(request.user, instance=ra)
            return render(request, "assessment-form.html",
                          {
                              "ra_form": ra_form,
                              "treatments": ra_form.fields["treatment"].queryset,
                              "sources": ra_form.fields["source"].queryset,
                              "exposures": ra_form.fields["exposure"].queryset
                          })
        return JsonResponse(ra.serialize(), safe=False)
    elif request.method == "POST":
        ra = RiskAssessment.objects.get(id=risk_assessment_id)
        ra_form = RAForm(request.user, request.POST, instance=ra)
        if ra_form.is_valid():
            new_assessment(request.user, ra_form)
            return HttpResponseRedirect(reverse("assessment"))
    elif request.method == "DELETE":
        RiskAssessment.objects.get(id=risk_assessment_id).delete()
        return HttpResponseRedirect(reverse("assessment"))


def new_assessment(user, ra_form):
    assessment = ra_form.save(commit=False)
    assessment.user = user
    assessment.source = ra_form.cleaned_data["source"]
    assessment.exposure = ra_form.cleaned_data["exposure"]
    assessment.save()
    assessment.treatment.set(ra_form.cleaned_data["treatment"])
    assessment.save()
    return assessment


class RAFormStep1(forms.ModelForm):
    class Meta:
        model = RiskAssessment
        fields = ["name", "description"]


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


class RAFormStep3(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RAFormStep3, self).__init__(*args, **kwargs)
        self.fields[
            "treatment"
        ].help_text = "Please select your treatment configuration"
        self.helper = FormHelper()

    class Meta:
        model = RiskAssessment
        fields = ["treatment"]
        widgets = {
            "treatment": forms.CheckboxSelectMultiple(),
        }


class RAFormStep4(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RAFormStep4, self).__init__(*args, **kwargs)

        self.fields["exposure"].empty_label = None
        self.fields["exposure"].help_text = "Please define your exposure scenario"
        self.helper = FormHelper()

    class Meta:
        model = RiskAssessment
        fields = ["exposure"]
        widgets = {
            "exposure": forms.RadioSelect(attrs={"empty_label": None}),
        }


class RAFormWizard(SessionWizardView):
    form_list = [RAFormStep1, RAFormStep2, RAFormStep3, RAFormStep4]
    template_name = "assessment-steps/step1.html"  # Default, can be overridden
    TEMPLATES = {
        "0": "assessment-steps/step1.html",
        "1": "assessment-steps/step2.html",
        "2": "assessment-steps/step3.html",
        "3": "assessment-steps/step4.html",
    }

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == '1':
            context.update({'sources': WaterSource.objects.filter(
                Q(user__exact=self.request.user) | Q(user__isnull=True)
            ).order_by("id")})
        elif self.steps.current == '2':
            context.update({'treatments': (
                Treatment.objects.filter(
                    Q(user__exact=self.request.user) | Q(user__isnull=True)
                )
                .order_by("id")
                .order_by("category")
            )})
        elif self.steps.current == '3':
            context.update({'exposures': ExposureScenario.objects.filter(
                Q(user__exact=self.request.user) | Q(user__isnull=True)
            ).order_by("id")})
        return context

    def done(self, form_list, **kwargs):
        all_cleaned_data = {}
        for form in form_list:
            all_cleaned_data.update(form.cleaned_data)

        # Extract treatments for later (before we pop them)
        treatments = all_cleaned_data.pop('treatment', [])

        # Get the current user from the request
        current_user = self.request.user

        # Now you can use `all_cleaned_data` to save the RiskAssessment instance or perform other operations.
        risk_assessment = RiskAssessment(**all_cleaned_data)

        # Set the user field to the current user
        risk_assessment.user = current_user

        risk_assessment.save()

        # Set the many-to-many field treatments using set()
        risk_assessment.treatment.set(treatments)

        return HttpResponseRedirect(reverse("index"))
        # Save your model instance or perform other operations
        # This method is called after completing all the steps


@login_required(login_url="/login")
def export_summary(request, risk_assessment_id):
    ra = RiskAssessment.objects.get(id=risk_assessment_id)
    if ra.user == request.user:
        results_long = simulate_risk(ra)
        results_long.rename(columns={"value": "infection_prob"}, inplace=True)
        results_long["pathogen"] = results_long["variable"].str.split("_", expand=True)[
            0
        ]
        results_long["stat"] = results_long["variable"].str.split("_", expand=True)[1]

        health = read_frame(Health.objects.all())
        results_long = pd.merge(results_long, health, on="pathogen")
        results_long["DALYs pppy"] = (
                results_long.infection_prob
                * results_long.infection_to_illness.astype(float)
                * results_long.dalys_per_case.astype(float)
        )
        results_long = results_long.groupby(["pathogen", "stat"]).describe(
            percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]
        )[["infection_prob", "DALYs pppy"]]
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
                "attachment; filename=" + str(ra.name) + "_summary.csv"
        )

        # results_long.to_csv(path_or_buf=response, sep=',',float_format='%.2f', index=False, decimal=".")
        results_long.to_csv(path_or_buf=response, sep=",", decimal=".")

        return response
    else:
        return HttpResponseRedirect(reverse("login"))


@login_required(login_url="/login")
def calculate_risk(request, risk_assessment_id):
    ra = RiskAssessment.objects.get(id=risk_assessment_id)
    # Selecting inflow concentration based in source water type
    df_inflow = read_frame(
        Inflow.objects.filter(water_source=ra.source).values(
            "min", "max", "pathogen__name", "water_source__name"
        )
    )
    df_inflow = df_inflow[
        df_inflow["pathogen__name"].isin(
            ["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"]
        )
    ]
    # Querying for Logremoval based on selected treatments
    df_treatment = read_frame(
        LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values(
            "min", "max", "treatment__name", "pathogen_group__pathogen_group"
        )
    )

    results_long = simulate_risk(ra)
    # results_long["value"] = round(results_long["value"],1)

    results_long["pathogen"] = results_long["variable"].str.split("_", expand=True)[0]
    results_long["stat"] = results_long["variable"].str.split("_", expand=True)[1]

    health = read_frame(Health.objects.all())
    results_long = pd.merge(results_long, health, on="pathogen")
    results_long["DALYs pppy"] = (
            results_long.value
            * results_long.infection_to_illness.astype(float)
            * results_long.dalys_per_case.astype(float)
    )
    summary = results_long.groupby(["pathogen", "stat"]).mean()
    risk = sum(summary["value"] > 10 ** -4) > 0
    dalyrisk = sum(summary["DALYs pppy"] > 10 ** -6) > 0

    if risk:
        bgcolor = "rgba(245, 0, 0, 0.15)"
        lcolor = "firebrick"
    else:
        bgcolor = None
        lcolor = "#0003e2"

    if dalyrisk:
        dalybgcolor = "rgba(245, 0, 0, 0.15)"
        dlcolor = "firebrick"
    else:
        dalybgcolor = None
        dlcolor = "#0003e2"

    risk_colors = ["#78BEF9", "#8081F1", "#5F60B3"]
    risk_colors_extended = [
        "#78BEF9",
        "#8081F1",
        "#5F60B3",
        "#3D3E73",
        "#F29C99",
        "#7375D9",
        "#CBCCF4",
    ]

    fig = px.box(
        results_long,
        x="stat",
        y="value",
        color="pathogen",
        points=False,
        log_y=True,
        color_discrete_sequence=risk_colors,
        hover_data={'value': ':.2e'}
    )

    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        plot_bgcolor=bgcolor,
        xaxis_title="",
        yaxis_title="Probability of infection per year",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    fig.add_hline(y=0.0001, line_dash="dashdot", line=dict(color=lcolor, width=3))
    fig.update_traces(
        marker_size=8
    )

    risk_plot = plot(fig, output_type="div", config={'displayModeBar': False})

    fig = px.box(
        results_long,
        x="stat",
        y="DALYs pppy",
        color="pathogen",
        points=False,
        log_y=True,
        color_discrete_sequence=risk_colors,
    )

    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        xaxis_title="",
        yaxis_title="DALYs pppy",
        plot_bgcolor=dalybgcolor,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    fig.add_hline(y=0.000001, line_dash="dashdot", line=dict(color=dlcolor, width=3))
    fig.update_traces(
        marker_size=8
    )
    daly_plot = plot(fig, output_type="div", config={'displayModeBar': False})

    # reshaping dataframe for plotting
    df_inflow2 = pd.melt(
        df_inflow, ("pathogen__name", "water_source__name")
    )
    df_inflow2 = df_inflow2[
        df_inflow2.pathogen__name.isin(
            ["Rotavirus", "Cryptosporidium parvum", "Campylobacter jejuni"]
        )
    ]
    df_inflow2 = df_inflow2.rename(
        columns={"pathogen__name": "Pathogen", "variable": ""}
    )
    fig2 = px.bar(
        df_inflow2,
        x="",
        y="value",
        log_y=True,
        facet_col="Pathogen",
        barmode="group",
        category_orders={
            "Pathogen": ["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"]
        },
        color_discrete_sequence=risk_colors_extended,
    )

    fig2.for_each_annotation(
        lambda a: a.update(
            text=a.text.split("=")[-1], font=dict(size=10, color="black"),
        )
    )

    fig2.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        yaxis_title="Source water concentraitons in N/L",
        margin=dict(l=0, r=0, t=40, b=0),
    )

    plot_div2 = plot(fig2, output_type="div", config={'displayModeBar': False})

    # reshaping
    df = pd.melt(df_treatment, ("treatment__name", "pathogen_group__pathogen_group"))
    df = df.rename(
        columns={
            "treatment__name": "Treatment",
            "pathogen_group__pathogen_group": "Pathogen Group",
            "variable": "",
        }
    )
    fig = px.bar(
        df,
        x="",
        y="value",
        color="Treatment",
        facet_col="Pathogen Group",
        category_orders={"Pathogen Group": ["Viruses", "Bacteria", "Protozoa"]},
        color_discrete_sequence=risk_colors_extended,
    )

    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=13))
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="top",
                    xanchor="center",
                    x=0.5, ),
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        yaxis_title="Logremoval of individual treatment step",
    )

    plot_div = plot(fig, output_type="div", config={'displayModeBar': False})

    return render(
        request,
        "assessment-result.html",
        {
            "plot_div": plot_div,
            "plot_div2": plot_div2,
            "daly_plot": daly_plot,
            "risk_plot": risk_plot,
            "ra": ra,
            "risk": risk,
            "dalyrisk": risk
        },
    )


def annual_risk(nexposure, event_probs):
    return 1 - np.prod(1 - np.random.choice(event_probs, nexposure, True))


def simulate_risk(ra):
    # Selecting inflow concentration based in source water type
    df_inflow = read_frame(
        Inflow.objects.filter(water_source=ra.source).values(
            "min", "max", "pathogen__name", "water_source__name"
        )
    )
    df_inflow = df_inflow[
        df_inflow["pathogen__name"].isin(
            ["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"]
        )
    ]
    # Querying dose response parameters based on pathogen inflow
    dr_models = read_frame(
        DoseResponse.objects.filter(
            pathogen__in=Pathogen.objects.filter(
                name__in=df_inflow["pathogen__name"]
            )
        )
    )

    # Querying for Logremoval based on selected treatments
    df_treatment = read_frame(
        LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values(
            "min", "max", "treatment__name", "pathogen_group__pathogen_group"
        )
    )

    # Summarizing treatment to treatment max and treatment min
    # df_treatment_summary=df_treatment.groupby(["pathogen_group__pathogen_group"]).sum().reset_index()
    df_treatment_summary = (
        df_treatment.groupby(["pathogen_group__pathogen_group"])[["min", "max"]]
        .apply(lambda x: x.sum())
        .reset_index()
    )

    results = pd.DataFrame()

    for index, row in df_inflow.iterrows():
        d = df_inflow.loc[df_inflow["pathogen__name"] == row["pathogen__name"]]
        dr = dr_models.loc[dr_models["pathogen"] == row["pathogen__name"]]

        if row["pathogen__name"] == "Rotavirus":
            selector = "Viruses"
        elif row["pathogen__name"] == "Cryptosporidium parvum":
            selector = "Protozoa"
        else:
            selector = "Bacteria"
        # result.append(selector)

        df_treat = df_treatment_summary[
            df_treatment_summary["pathogen_group__pathogen_group"] == selector
            ]

        risk_df = pd.DataFrame(
            {
                "inflow": np.random.normal(
                    loc=(
                                np.log10(float(d["min"]) + 10 ** (-8))
                                + np.log10(float(d["max"]))
                        )
                        / 2,
                    scale=(
                                  np.log10(float(d["max"]))
                                  - np.log10(float(d["min"]) + 10 ** (-8))
                          )
                          / 4,
                    size=10000,
                ),
                "LRV": np.random.uniform(
                    low=df_treat["min"], high=df_treat["min"], size=10000
                ),
                "LRVmax": np.random.uniform(
                    low=df_treat["max"], high=df_treat["max"], size=10000
                ),
            }
        )
        risk_df["outflow"] = risk_df["inflow"] - risk_df["LRV"]
        risk_df["outflow_min"] = risk_df["inflow"] - risk_df["LRVmax"]

        risk_df["dose"] = (10 ** risk_df["outflow"]) * float(
            ra.exposure.volume_per_event
        )
        risk_df["dose_min"] = (10 ** risk_df["outflow_min"]) * float(
            ra.exposure.volume_per_event
        )

        if selector != "Protozoa":
            risk_df["probs"] = 1 - (
                    1 + (risk_df["dose"]) * (2 ** (1 / float(dr.alpha)) - 1) / float(dr.n50)
            ) ** -float(dr.alpha)
            risk_df["probs_min"] = 1 - (
                    1
                    + (risk_df["dose_min"])
                    * (2 ** (1 / float(dr.alpha)) - 1)
                    / float(dr.n50)
            ) ** -float(dr.alpha)

        else:
            risk_df["probs"] = 1 - np.exp(-float(dr.k) * (risk_df["dose"]))
            risk_df["probs_min"] = 1 - np.exp(-float(dr.k) * (risk_df["dose_min"]))

        results[row["pathogen__name"] + "_MinimumLRV"] = [
            annual_risk(int(ra.exposure.events_per_year), risk_df["probs"])
            for _ in range(1000)
        ]
        results[row["pathogen__name"] + "_MaximumLRV"] = [
            annual_risk(int(ra.exposure.events_per_year), risk_df["probs_min"])
            for _ in range(1000)
        ]

    results_long = pd.melt(results)
    results_long["log probability"] = np.log10(results_long["value"])
    return results_long


@login_required(login_url="/login")
def comparison_view(request):
    user = request.user
    if request.method == "POST":
        form = ComparisonForm(user, request.POST)
        if form.is_valid():
            comparison = Comparison()
            comparison.save()
            comparison.risk_assessment.set(form.cleaned_data["risk_assessment"])
            results = []
            ras = comparison.risk_assessment.all()
            for i in range(len(ras)):
                sim = simulate_risk(ras[i])
                sim["Assessment"] = ras[i].name
                results.append(sim)

            df = pd.concat(results)

            df["pathogen"] = df["variable"].str.split("_", expand=True)[0]
            df["stat"] = df["variable"].str.split("_", expand=True)[1]
            dfmin = (
                df.groupby(["pathogen", "Assessment"])
                .min("value")
                .reset_index()
                .assign(stat="min")
            )
            dfmax = (
                df.groupby(["pathogen", "Assessment"])
                .max("value")
                .reset_index()
                .assign(stat="max")
            )
            df_summary = dfmin.append(dfmax).sort_values(by="value", ascending=False)
            df_mean = (
                df.groupby(["pathogen", "Assessment", "stat"])
                .mean("value")
                .reset_index()
                .sort_values(by="value", ascending=False)
            )

            fig = plot_comparison(df_summary, df_mean)

            risk_plot = plot(fig, output_type="div", config={'displayModeBar': False})

            return render(
                request,
                "assessment-result.html",
                {"risk_plot": risk_plot, "comparison": True},
            )
    else:
        form = ComparisonForm(user=user)
    return render(request, "comparison.html", {"form": form})


def plot_comparison(df, df2):
    fig = px.box(
        df,
        x="Assessment",
        y="value",
        color="pathogen",
        log_y=True,
        color_discrete_sequence=[
            "#78BEF9",
            "#8081F1",
            "#5F60B3",
            "#3D3E73",
            "#F29C99",
            "#7375D9",
            "#CBCCF4",
        ],
    )

    fig.add_traces(
        list(
            px.box(
                df2,
                x="Assessment",
                y="value",
                color="pathogen",
                log_y=True,
                color_discrete_sequence=["#7375D9", "#7375D9", "#7375D9", "#7375D9"],
            ).select_traces()
        )
    )

    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        yaxis_title="Probability of infection per year",
        xaxis_title="",
        margin=dict(l=0, r=0, t=30, b=0),
        annotations=[
            go.Annotation(
                y=-4,
                x=1.2,
                text="Tolerable risk level of 1/10000 infections pppy",
                bgcolor="#0003e2",
                bordercolor="white",
                borderpad=5,
                font=dict(color="white"),
            )
        ],
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="black"),
            bgcolor="white",
            bordercolor="#007c9e",
            borderwidth=0,
        )
    )

    fig.add_hline(
        y=0.0001,
        line_dash="dashdot",
        line=dict(color="#0003e2", width=3),
    )

    fig.update_traces(
        marker_size=8, hovertemplate=None, hoverinfo="skip", line=dict(width=0)
    )
    return fig
