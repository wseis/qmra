from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from .forms import RAForm, SourceWaterForm,  TreatmentForm, ExposureForm, LogRemovalForm, InflowForm, ComparisonForm
from .models import *
from django.views.decorators.csrf import ensure_csrf_cookie
import numpy as np
import pandas as  pd
import plotly.express as px
from plotly.offline import plot
from django_pandas.io import read_frame
import decimal
import markdown2 as md

# Create your views here.

def about(request):
    content = Text.objects.get(title = "About") 
    return render(request, "qmratool/about.html", {"content":md.markdown(content.content)})

def qa(request):
    content = QA.objects.all() 
    return render(request, "qmratool/QA.html", {'content': content})

# Overview index page
def index(request):
    if request.user.is_authenticated:
        assessment = RiskAssessment.objects.filter(user = request.user)
    else:
        assessment=[]
        return HttpResponseRedirect(reverse('login'))
    return render(request, "qmratool/index.html", {"assessments": assessment})

def bayes(request):
    return render(request,  "bayes/bayes2.html")


# 
def comparison(request):
    user  = request.user
    if request.method == "POST":
        return HttpResponse("Post received")
    else:
        form = ComparisonForm(user=user)
    return render(request, 'qmratool/comparison.html', {"form":form})




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
        form=RAForm(user,  request.POST)
        if form.is_valid():
            assessment=RiskAssessment()
            assessment.user=user
            assessment.name=form.cleaned_data["name"]
            assessment.description=form.cleaned_data["description"]
            assessment.source=form.cleaned_data["source"]
            assessment.save()
            assessment.treatment.set(form.cleaned_data["treatment"])
            assessment.exposure= form.cleaned_data["exposure"]
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
            assessment.exposure= form.cleaned_data["exposure"]
            assessment.save()

            return HttpResponseRedirect(reverse('index'))    
            #return HttpResponseRedirect(reverse('source', args=(assessment.name,)))
        else:
            return HttpResponse(request, "Form not valid")
    else:
        ra = RiskAssessment.objects.get(id=ra_id)
        data = {"id": ra.id, "name":ra.name, "description":ra.description,"source": ra.source,
        "treatment":ra.treatment.all(), "exposure":ra.exposure}
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
            return HttpResponse(request, "Form not valid")
    else:
        SWform=SourceWaterForm()
        Inflowform = InflowForm()
        return render(request, "qmratool/source.html", { "SWform":SWform, "InflowForm": Inflowform})

# Treatment management
def treatment_create(request):
    user = request.user
    if request.method == "POST":
        form= TreatmentForm(request.POST)
        if form.is_valid():
            treatment=Treatment()
            treatment.user=user
            treatment.name = form.cleaned_data["name"]
            treatment.description=form.cleaned_data["description"]
            treatment.save()
            
            return HttpResponseRedirect(reverse("treatment_edit"))
            #return HttpResponse(request, form.cleaned_data["pathogen_group"])
        else:
            return HttpResponse(request, "Form not valid")
    else:
        TreatForm=TreatmentForm()
        #pathogen_groups = PathogenGroup.objects.all()
    return render(request, "qmratool/treatment.html", {"TreatForm": TreatForm })

def treatment_edit(request):
    user = request.user
    treatments = user.treatments.all()
    return render(request, "qmratool/treatment_edit.html", {"treatments": treatments})

def treatment_delete(request, treatment_id):
    Treatment.objects.get(id=treatment_id).delete()
    return HttpResponseRedirect(reverse('treatment_edit'))

def LRV_edit(request, treatment_id, pathogen_group_id):
    
    if request.method == "POST":
        pathogen_group = PathogenGroup.objects.get(id = pathogen_group_id)
        LRV = LogRemoval.objects.filter(treatment = Treatment.objects.get(id = treatment_id), pathogen_group= pathogen_group)
        if len(LRV) == 1:
            LogRemoval.objects.get(treatment = Treatment.objects.get(id = treatment_id), pathogen_group= pathogen_group).delete()
        form= LogRemovalForm(request.POST)
        if form.is_valid():
            logremoval=LogRemoval()
            logremoval.treatment= Treatment.objects.get(id = treatment_id)
            logremoval.min = form.cleaned_data["min"]
            logremoval.max=form.cleaned_data["max"]
            logremoval.pathogen_group = PathogenGroup.objects.get(id = pathogen_group_id)
            logremoval.reference=form.cleaned_data["reference"]
            logremoval.save()
            
            return HttpResponseRedirect(reverse("treatment_edit"))
        else:
            return HttpResponse(request, "Form not valid")
    else:
        ref = Reference.objects.get(id = 51)
        pathogen_group = PathogenGroup.objects.get(id = pathogen_group_id)
        LRV = LogRemoval.objects.filter(treatment = Treatment.objects.get(id = treatment_id), pathogen_group= pathogen_group)
        if len(LRV) == 1:
            LRV = LogRemoval.objects.get(treatment = Treatment.objects.get(id = treatment_id), pathogen_group= pathogen_group)
            LRVForm=LogRemovalForm({"pathogen_group": pathogen_group, "min":LRV.min, "max":LRV.max, "reference": ref })
        else:
            LRVForm=LogRemovalForm({"pathogen_group": pathogen_group, "min":0, "max":0, "reference": ref })

    return render(request, "qmratool/logremoval_edit.html", {"LRVForm": LRVForm,
    "pathogen_group_id": pathogen_group_id,
    "treatment_id": treatment_id,
    "pathogen": pathogen_group })




# Modelling risk

def calculate_risk(request, ra_id):
    ra = RiskAssessment.objects.get(id = ra_id)
    
    # Selecting inflow concentration based in source water type
    df_inflow = read_frame(Inflow.objects.filter(water_source=ra.source).values("min", "max", "pathogen__pathogen", "water_source__water_source_name"))
    
    # Querying dose response parameters based on pathogen inflow
    dr_models = read_frame(DoseResponse.objects.filter(pathogen__in=Pathogen.objects.filter(pathogen__in=df_inflow["pathogen__pathogen"])))
    
    # Querying for Logremoval based on selected treatments
    df_treatment=read_frame(LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values("min", "max", "treatment__name", "pathogen_group__pathogen_group"))
    
    #Querying for exposure scenario
    #exposure =read_frame(ra.exposure.all().values("events_per_year", "volume_per_event"))

    # Summarizing treatment to treatment max and treatment min
    df_treatment_summary=df_treatment.groupby(["pathogen_group__pathogen_group"]).sum().reset_index()
    
        # annual risk function
    def annual_risk(nexposure, event_probs):
        return 1-np.prod(1-np.random.choice(event_probs, nexposure, True))
    #df_inflow = df_inflow["pathogen__pathogen"].isin(["Rotavirus", "Cryptosporidium parvum", "Campylobacter jejuni"])
    
    results = pd.DataFrame()

    for index, row in df_inflow.iterrows():
        d = df_inflow.loc[df_inflow["pathogen__pathogen"] ==row["pathogen__pathogen"]]
        dr = dr_models.loc[dr_models["pathogen"]==row["pathogen__pathogen"]]

        if row["pathogen__pathogen"] == "Rotavirus":
            selector = "Viruses" 
        elif row["pathogen__pathogen"]== "Cryptosporidium parvum":
            selector = "Protozoa"
        else:
            selector = "Bacteria"
        #result.append(selector)

        df_treat = df_treatment_summary[df_treatment_summary["pathogen_group__pathogen_group"]==selector]



        risk_df = pd.DataFrame({"inflow": np.random.normal(loc=(np.log10(float(d["min"])+10**(-8))+np.log10(float(d["max"]) ))/2, 
                                                            scale = (np.log10(float(d["max"]))-np.log10(float(d["min"])+10**(-8) ))/4,  
                                                            size = 10000),
                                "LRV": np.random.uniform(low= df_treat["min"], 
                                                        high= df_treat["max"], 
                                                        size= 10000) })
        risk_df["outflow"]=risk_df["inflow"] - risk_df["LRV"]
        risk_df["dose"] = (10**risk_df["outflow"])*float(ra.exposure.volume_per_event)

        if selector != "Protozoa":
            risk_df["probs"] = 1 - (1 + (risk_df["dose"]) * (2 ** (1/float(dr.alpha)) - 1)/float(dr.n50)) ** -float(dr.alpha)
        else:
            risk_df["probs"] = 1 - np.exp(-float(dr.k)*(risk_df["dose"]))

        results[row["pathogen__pathogen"]] = [annual_risk(int(ra.exposure.events_per_year), risk_df["probs"] ) for _ in range(1000)]


    results_long = pd.melt(results)
    results_long["log probability"] = np.log10(results_long["value"])

    fig = px.box(results_long, x="variable", y="value",
                                points="all",  log_y =True, 
                                title="Risk as probability of infection per year",
                                color_discrete_sequence=["#007c9f", "#007c9f", "#007c9f"])

    #fig.update_layout(shapes=[
    #dict(
    #  type= 'line',
    #  y0= 0.03, y1= 0.03,
    #  x0 =-.5, x1=2.5,
    #  line=dict(
    #    color="MediumPurple",
    #    width=4,
    #    dash="dot") 
    #)
    #])

    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Risk assessment as probability of infection per year'},
        xaxis_title = "Reference Pathogen",
        yaxis_title = "Probability of infection per year",
        #markersize= 12,
        )

    fig.update_traces(marker_size = 8)#['#75c3ff', "red"],#, marker_line_color='#212c52',

    
    risk_plot = plot(fig, output_type = "div")


     # reshaping dataframe for plotting
    df_inflow2 =pd.melt(df_inflow, ("pathogen__pathogen", "water_source__water_source_name"))
    df_inflow2 = df_inflow2[df_inflow2.pathogen__pathogen.isin(["Rotavirus", "Cryptosporidium parvum", "Campylobacter jejuni"])]
    df_inflow2 = df_inflow2.rename(columns={"pathogen__pathogen": "Pathogen", "variable":""})
    fig2 = px.bar(df_inflow2, 
             x="", y = "value", 
             log_y=True,
            facet_col="Pathogen", 
            barmode="group", 
            category_orders={"Pathogen": ["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"]},
            color_discrete_sequence=["#007c9f", "rgb(0, 86, 100)", "grey", "red3", "steelblue"])

              
    fig2.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Inflow concentrations of referene pathogens'},
        yaxis_title = "Source water concentraitons in N/L",
        )
       
    plot_div2 = plot(fig2, output_type = "div")

    # reshaping     
    df = pd.melt(df_treatment, ("treatment__name", "pathogen_group__pathogen_group"))
    df = df.rename(columns = {"treatment__name": "Treatment", "pathogen_group__pathogen_group": "Pathogen Group", "variable":""})
    fig = px.bar(df, x="", y = "value", 
    color="Treatment", facet_col="Pathogen Group",
    category_orders={"Pathogen Group": ["Viruses", "Bacteria", "Protozoa"]},
    color_discrete_sequence=["#007c9f", "rgb(0, 86, 100)", "grey"])
    #title="Log-removal of selected treatment train")
    fig.update_layout(legend=dict(
                 orientation="h",
                 yanchor="top",
                 y=-.1,
                 xanchor="left",
                x=0))


    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Inflow concentrations of referene pathogens'},
        
        yaxis_title = "Logremoval of individual treatment step",
        )


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




def api_treatments(request):
    treatments = Treatment.objects.filter(user__in = [request.user, 8])
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([treatment.serialize() for treatment in treatments], safe=False)

    
def api_treatments_by_id(request, treatment_id):
    treatments = Treatment.objects.filter(id = treatment_id)
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([treatment.serialize() for treatment in treatments], safe=False)

def api_sources_by_id(request, source_id):
    sources = SourceWater.objects.filter(id = source_id)
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([source.serialize() for source in sources], safe=False)

def api_exposure_by_id(request, exposure_id):
    exposures = Exposure.objects.filter(id = exposure_id)
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([exposure.serialize() for exposure in exposures], safe=False)