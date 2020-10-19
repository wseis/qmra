from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from .forms import RAForm, SourceWaterForm, TreatmentForm, ExposureForm
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
    return render(request, 'qmratool/new_ra.html', {"form":form})


def calculate_risk(request, ra_id):
    ra = RiskAssessment.objects.get(id = ra_id)
    df_inflow = read_frame(Inflow.objects.filter(water_source=ra.source).values("min", "max", "pathogen__pathogen", "water_source__water_source_name"))
    df_inflow =pd.melt(df_inflow, ("pathogen__pathogen", "water_source__water_source_name"))
    fig2 = px.bar(df_inflow, x="variable", y = "value", 
    color="pathogen__pathogen", 
    title="Inflow concentration")
    plot_div2 = plot(fig2, output_type = "div")
    
    df=read_frame(LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values("min", "max", "treatment__name", "pathogen_group__pathogen_group"))
    df = pd.melt(df, ("treatment__name", "pathogen_group__pathogen_group"))
    
    fig = px.bar(df, x="variable", y = "value", 
    color="treatment__name", facet_col="pathogen_group__pathogen_group",
    title="Log-removal of selected treatment train")
    plot_div = plot(fig, output_type = "div")
    
    return render(request,"qmratool/results.html", {"plot_div":plot_div, "plot_div2":plot_div2})













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
