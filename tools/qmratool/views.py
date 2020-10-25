from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from .forms import RAForm, SourceWaterForm, TreatmentForm, ExposureForm, RAForm2
from .models import *
from django.views.decorators.csrf import ensure_csrf_cookie
import numpy as np
import pandas as  pd
import plotly.express as px
from plotly.offline import plot
from django_pandas.io import read_frame
# Create your views here.




def index(request):
    if request.user.is_authenticated:
        assessment = RiskAssessment.objects.filter(user = request.user)
    else:
        assessment=[]
        return HttpResponseRedirect(reverse('login'))
    return render(request, "qmratool/index.html", {"assessments": assessment})

def new_assessment(request):
    user = request.user
    if request.method == "POST":
        form=RAForm(request.POST)
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
        form = RAForm()
        sw_form = RAForm2()
    return render(request, 'qmratool/new_ra.html', {"form":form, "sw_form": sw_form})


def edit_assessment(request, ra_id):
    user = request.user
    if request.method == "POST":
        form=RAForm(request.POST)
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
        data = {"name":ra.name, "description":ra.description,"source": ra.source,
        "treatment":ra.treatment.all(), "exposure":ra.exposure.all()}
        form = RAForm(data)
        
    return render(request, 'qmratool/edit_ra.html', {"form":form, "ra_id":ra.id})


def delete_assessment(request, ra_id):
    RiskAssessment.objects.get(id=ra_id).delete()
    return HttpResponseRedirect(reverse('index'))    
    


def calculate_risk(request, ra_id):
    ra = RiskAssessment.objects.get(id = ra_id)
    
    df_inflow = read_frame(Inflow.objects.filter(water_source=ra.source).values("min", "max", "pathogen__pathogen", "water_source__water_source_name"))
    dr_models = read_frame(DoseResponse.objects.filter(pathogen__in=Pathogen.objects.filter(pathogen__in=df_inflow["pathogen__pathogen"])))
       
    df_inflow2 =pd.melt(df_inflow, ("pathogen__pathogen", "water_source__water_source_name"))
    fig2 = px.bar(df_inflow2, x="variable", y = "value", 
    color="pathogen__pathogen", barmode="group",
    title="Inflow concentration")
    plot_div2 = plot(fig2, output_type = "div")
    
    df_treatment=read_frame(LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values("min", "max", "treatment__name", "pathogen_group__pathogen_group"))
    df = pd.melt(df_treatment, ("treatment__name", "pathogen_group__pathogen_group"))
    
    fig = px.bar(df, x="variable", y = "value", 
    color="treatment__name", facet_col="pathogen_group__pathogen_group",
    title="Log-removal of selected treatment train")
    plot_div = plot(fig, output_type = "div")
    
    df_treatment_summary=df_treatment.groupby(["pathogen_group__pathogen_group"]).sum()

    # Selecting pathogen
    samples = pd.DataFrame({"inflow": np.random.normal(loc=(np.log10(df_inflow["min"][0]) + np.log10(df_inflow["max"][0]))/2, 
                                                        scale= (np.log10(df_inflow["max"][0])-np.log10(df_inflow["min"][0]))/4, 
                                                        size= 1000),
                            "LRV": np.random.uniform(low= df_treatment_summary["min"][0], 
                                                        high= df_treatment_summary["max"][0], 
                                                        size= 1000)})
    samples["outflow"]=samples["inflow"] - samples["LRV"]

    alpha = 0.14
    N50 = 850

    samples["probs"] = 1 - (1 + (10**samples["outflow"]) * (2 ** (1/alpha) - 1)/N50) ** -alpha

    def annual_risk(nexposure, event_probs):
        return 1-np.prod(1-np.random.choice(event_probs, nexposure, True))
    
    res = [annual_risk(50, samples["probs"] ).round(3) for _ in range(1000)]

    samples["res"]= res
    hist_inflow = px.histogram(samples, x = "inflow")
    hist_inflow = plot(hist_inflow, output_type="div")
    hist_outflow = px.histogram(samples, x = "outflow")
    hist_outflow = plot(hist_outflow, output_type="div")
    hist_prob = px.histogram(samples, x = "probs")
    hist_prob = plot(hist_prob, output_type="div")

    hist_res = px.histogram(samples, x = "res")
    hist_res = plot(hist_res, output_type = "div")
    

    return render(request,"qmratool/results.html", {"plot_div":plot_div, 
    "plot_div2":plot_div2, 
    "data":df_inflow.to_html(),
    "summary":df_treatment_summary.to_html(),
    "samples":df_treatment.to_html,
    "dr_models":dr_models.to_html(),
    "hist_inflow":hist_inflow,
    "hist_outflow":hist_outflow,
    "hist_prob":hist_prob,
    "hist_res":hist_res})



def source(request, ra_name):
    sources = SourceWater.objects.all()
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
        form=SourceWaterForm()
        return render(request, "qmratool/source.html", { "ra_name":ra_name, "sources":sources, "form":form})


def treatment(request, ra_id):
    if request.method == "POST":
        form=TreatmentForm(request.POST)
        if form.is_valid():
            assessment=RiskAssessment.objects.get(id = ra_id)
            assessment.treatment.add(form.cleand_data)
            assessment.save()
        else:
            return HttpResponse("Form not valid")
    else:
        form=TreatmentForm()
    return render(request, "qmratool/treatment.html", {"form": form, "ra_id":ra_id})





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
