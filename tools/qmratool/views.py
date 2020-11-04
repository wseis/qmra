from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from .forms import RAForm, SourceWaterForm, TreatmentForm, ExposureForm, LogRemovalForm, InflowForm
from .models import *
from django.views.decorators.csrf import ensure_csrf_cookie
import numpy as np
import pandas as  pd
import plotly.express as px
from plotly.offline import plot
from django_pandas.io import read_frame
import decimal
from django.views.generic.edit import CreateView

# Create your views here.


# Overview index page
def index(request):
    if request.user.is_authenticated:
        assessment = RiskAssessment.objects.filter(user = request.user)
    else:
        assessment=[]
        return HttpResponseRedirect(reverse('login'))
    return render(request, "qmratool/index.html", {"assessments": assessment})


# Exposure Scenario managememt
def create_scenario(request):
    user = request.user
    if request.method == "POST":
        form= ExposureForm(request.POST)
        if form.is_valid():
            exposure=Exposure()
            exposure.user=user
            exposure.name = form.cleaned_data["name"]
            exposure.description=form.cleaned_data["description"]
            exposure.volume_per_event=form.cleaned_data["volume_per_event"]
            exposure.events_per_year=form.cleaned_data["events_per_year"]
            exposure.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponse(request, "Form not valid")
    else:
        form=ExposureForm
    return render(request, "qmratool/scenario_create.html",{"form":form})


def edit_scenario(request):
    user = request.user
    scenarios = user.scenarios.all()
    return render(request, "qmratool/scenario_edit.html", {"scenarios":scenarios})


def delete_scenario(request, scenario_id):
    Exposure.objects.get(id=scenario_id).delete()
    return HttpResponseRedirect(reverse('scenario_edit'))


# Risk assessment management
def new_assessment(request):
    user = request.user
    if request.method == "POST":
        form=RAForm(user,request.POST)
        if form.is_valid():
            assessment=RiskAssessment()
            assessment.user=user
            assessment.name=form.cleaned_data["name"]
            assessment.description=form.cleaned_data["description"]
            assessment.source=form.cleaned_data["source"]
            assessment.save()
            assessment.treatment.set(form.cleaned_data["treatment"])
            assessment.exposure.set(form.cleaned_data["exposure"])
            assessment.save()

            return HttpResponseRedirect(reverse('index'))    
            #return HttpResponseRedirect(reverse('source', args=(assessment.name,)))
        else:
            return HttpResponse(request, "Form not valid")
    else:
        form = RAForm(user)
        content = Treatment.objects.all()
       
    return render(request, 'qmratool/new_ra.html', {"form":form, "content":content})


def edit_assessment(request, ra_id):
    user = request.user
    if request.method == "POST":
        form=RAForm(user, request.POST)
        RiskAssessment.objects.get(id=ra_id).delete()
        if form.is_valid():
            assessment=RiskAssessment()
            assessment.user=user
            assessment.name=form.cleaned_data["name"]
            assessment.description=form.cleaned_data["description"]
            assessment.source=form.cleaned_data["source"]
            assessment.save()
            assessment.treatment.set(form.cleaned_data["treatment"])
            assessment.exposure.set(form.cleaned_data["exposure"])
            assessment.save()

            return HttpResponseRedirect(reverse('index'))    
            #return HttpResponseRedirect(reverse('source', args=(assessment.name,)))
        else:
            return HttpResponse(request, "Form not valid")
    else:
        ra = RiskAssessment.objects.get(id=ra_id)
        data = {"id": ra.id, "name":ra.name, "description":ra.description,"source": ra.source,
        "treatment":ra.treatment.all(), "exposure":ra.exposure.all()}
        form = RAForm(user, data)
        
    return render(request, 'qmratool/edit_ra.html', {"form":form, "ra_id":ra.id})


def delete_assessment(request, ra_id):
    RiskAssessment.objects.get(id=ra_id).delete()
    return HttpResponseRedirect(reverse('index'))    

# Source water management
def source_create(request):
    
    if request.method=="POST":
        form=SourceWaterForm(request.POST)
        if form.is_valid():
            assessment=RiskAssessment.objects.get(user = request.user, name = ra_name)
           # 
            assessment.source = form.cleaned_data["sourcewater"]#SourceWater.objects.get(sourcewater=form.cleaned_data["sourcewater"])
            assessment.save()
            return HttpResponseRedirect(reverse('treatment', args=(assessment.id,)))
        else:
            return HttpResponse(request, "Form not valid")
    else:
        SWform=SourceWaterForm()
        Inflowform = InflowForm()
        return render(request, "qmratool/source.html", { "SWform":SWform, "InflowForm": Inflowform})

# Treatment management
def treatment_create(request):
    if request.method == "POST":
        form=TreatmentForm(request.POST)
        if form.is_valid():
            assessment=RiskAssessment.objects.get(id = ra_id)
            assessment.treatment.add(form.cleand_data)
            assessment.save()
        else:
            return HttpResponse("Form not valid")
    else:
        TreatForm=TreatmentForm()
        LRVForm = LogRemovalForm()
    return render(request, "qmratool/treatment.html", {"TreatForm": TreatForm, "LRVForm": LRVForm })


 



# Modelling risk

def calculate_risk(request, ra_id):
    ra = RiskAssessment.objects.get(id = ra_id)
    
    # Selecting inflow concentration based in source water type
    df_inflow = read_frame(Inflow.objects.filter(water_source=ra.source).values("min", "max", "pathogen__pathogen", "water_source__water_source_name"))
    
    # Querying dose response parameters based on pathogen inflow
    dr_models = read_frame(DoseResponse.objects.filter(pathogen__in=Pathogen.objects.filter(pathogen__in=df_inflow["pathogen__pathogen"])))
    
    # Querying for Logremoval based on selected treatments
    df_treatment=read_frame(LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values("min", "max", "treatment__name", "pathogen_group__pathogen_group"))
    
    # Summarizing treatment to treatment max and treatment min
    df_treatment_summary=df_treatment.groupby(["pathogen_group__pathogen_group"]).sum().reset_index()
    
    # annual risk function
    def annual_risk(nexposure, event_probs):
        return 1-np.prod(1-np.random.choice(event_probs, nexposure, True))
    #df_inflow = df_inflow["pathogen__pathogen"].isin(["Rotavirus", "Cryptosporidium parvum", "Campylobacter jejuni"])
    
    results = pd.DataFrame()
    for pathogen in ["Rotavirus", "Cryptosporidium parvum", "Campylobacter jejuni"]:#df_inflow["pathogen__pathogen"]:
        d = df_inflow.loc[df_inflow["pathogen__pathogen"] == pathogen]
        dr = dr_models.loc[dr_models["pathogen"]==pathogen]
        #result.append(pathogen)

        if pathogen == "Rotavirus":
            selector = "Viruses"
        elif pathogen == "Cryptosporidium parvum":
            selector = "Protozoa"
        else:
            selector = "Bacteria"
        #result.append(selector)

        df_treat = df_treatment_summary[df_treatment_summary["pathogen_group__pathogen_group"]==selector]
                                    
                                                         

        risk_df = pd.DataFrame({"inflow": np.random.normal(loc=(np.log10(float(d["min"]))+np.log10(float(d["max"]) ))/2, 
                                                            scale = (np.log10(float(d["max"]))-np.log10(float(d["min"]) ))/4,  
                                                            size = 1000),
                                "LRV": np.random.uniform(low= df_treat["min"], 
                                                         high= df_treat["max"], 
                                                         size= 1000) })
        risk_df["outflow"]=risk_df["inflow"] - risk_df["LRV"]
       
        if selector != "Protozoa":
            risk_df["probs"] = 1 - (1 + (10**risk_df["outflow"]) * (2 ** (1/float(dr.alpha)) - 1)/float(dr.n50)) ** -float(dr.alpha)
        else:
            risk_df["probs"] = 1 - np.exp(-float(dr.k)*(10**risk_df["outflow"]))
        
        results[pathogen] = [annual_risk(1, risk_df["probs"] ).round(3) for _ in range(1000)]

    results_long = pd.melt(results)
    results_long["log probability"] = np.log10(results_long["value"])
    fig = px.box(results_long, x="variable", y="log probability", 
                                points="all", 
                                title="Risk assessment as probability of infection per year",
                                color_discrete_sequence=["#007c9f", "#007c9f", "#007c9f"])
    risk_plot = plot(fig, output_type = "div")


     # reshaping dataframe for plotting
    df_inflow2 =pd.melt(df_inflow, ("pathogen__pathogen", "water_source__water_source_name"))
    df_inflow2 = df_inflow2[df_inflow2.pathogen__pathogen.isin(["Rotavirus", "Cryptosporidium parvum", "Campylobacter jejuni"])]
    fig2 = px.bar(df_inflow2, x="variable", y = "value", log_y=True,
    facet_col="pathogen__pathogen", barmode="group", 
    color_discrete_sequence=["#007c9f", "rgb(0, 86, 100)", "grey", "red3", "steelblue"],
    
    title="Inflow concentration")
    plot_div2 = plot(fig2, output_type = "div")

    # reshaping     
    df = pd.melt(df_treatment, ("treatment__name", "pathogen_group__pathogen_group"))
    fig = px.bar(df, x="variable", y = "value", 
    color="treatment__name", facet_col="pathogen_group__pathogen_group",
    color_discrete_sequence=["#007c9f", "rgb(0, 86, 100)", "grey"],
    title="Log-removal of selected treatment train")
    fig.update_layout(legend=dict(
                     orientation="h",
                     yanchor="bottom",
                     y=1.1,
                     xanchor="right",
                    x=1))
    plot_div = plot(fig, output_type = "div")
    
   

    return render(request,"qmratool/results.html", {"plot_div":plot_div, 
    "plot_div2":plot_div2, 
    #"data":df_inflow.to_html(),
    #"summary":df_treatment_summary.to_html(),
    #"samples":df_treatment.to_html,
    "risk_plot": risk_plot
    })


# Registration and user management
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "qmratool/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "qmratool/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "qmratool/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "qmratool/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "qmratool/register.html")
