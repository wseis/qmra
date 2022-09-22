from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render

from qmratool.helper_functions import plot_comparison

from .forms import RAForm, SourceWaterForm,  TreatmentForm, ExposureForm, LogRemovalForm, InflowForm, ComparisonForm
from .models import *

import numpy as np
import pandas as  pd
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go
from django_pandas.io import read_frame

import markdown2 as md
from django.db import IntegrityError

from django.contrib.auth.decorators import login_required
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


@login_required(login_url="/login")
def comparison(request):
    user  = request.user
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
            dfmin = df.groupby(["pathogen", "Assessment"]).min("value").reset_index().assign(stat = "min")
            dfmax = df.groupby(["pathogen", "Assessment"]).max("value").reset_index().assign(stat = "max")
            df_summary = dfmin.append(dfmax).sort_values(by = "value", ascending = False)
            df_mean = df.groupby(["pathogen", "Assessment", "stat"]).mean("value").reset_index().sort_values(by = "value", ascending = False)

            fig = plot_comparison(df_summary, df_mean)

            risk_plot = plot(fig, output_type = "div")


            return render(request, "qmratool/results.html",  {"risk_plot": risk_plot, "comparison": True})
    else:
        form = ComparisonForm(user=user)
    return render(request, 'qmratool/comparison.html', {"form":form})




# Exposure Scenario managememt
@login_required(login_url="/login")
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

@login_required(login_url="/login")
def edit_scenario(request):
    user = request.user
    scenarios = user.scenarios.all()
    return render(request, "qmratool/scenario_edit.html", {"scenarios":scenarios})

@login_required(login_url="/login")
def delete_scenario(request, scenario_id):
    Exposure.objects.get(id=scenario_id).delete()
    return HttpResponseRedirect(reverse('scenario_edit'))


# Risk assessment management
@login_required(login_url="/login")
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

@login_required(login_url="/login")
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

@login_required(login_url="/login")
def delete_assessment(request, ra_id):
    RiskAssessment.objects.get(id=ra_id).delete()
    return HttpResponseRedirect(reverse('index'))    

# Source water management
@login_required(login_url="/login")
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
@login_required(login_url="/login")
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

@login_required(login_url="/login")
def treatment_edit(request):
    user = request.user
    treatments = user.treatments.all()
    return render(request, "qmratool/treatment_edit.html", {"treatments": treatments})

@login_required(login_url="/login")
def treatment_delete(request, treatment_id):
    Treatment.objects.get(id=treatment_id).delete()
    return HttpResponseRedirect(reverse('treatment_edit'))

@login_required(login_url="/login")
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


# Exporting risk assessment results

@login_required(login_url="/login")
def export_summary(request, ra_id):
    
    ra = RiskAssessment.objects.get(id = ra_id)
    if ra.user == request.user:
        results_long = simulate_risk(ra)
        results_long.rename(columns = {'value':'infection_prob'}, inplace = True)
        results_long["pathogen"] = results_long["variable"].str.split("_", expand=True)[0]
        results_long["stat"] = results_long["variable"].str.split("_", expand=True)[1]

        health = read_frame(Health.objects.all())
        results_long = pd.merge(results_long, health, on = "pathogen")
        results_long["DALYs pppy"] = results_long.infection_prob*results_long.infection_to_illness.astype(float)*results_long.dalys_per_case.astype(float)
        results_long = results_long.groupby(["pathogen", "stat"]).describe(percentiles = [.05, 0.25, 0.5, 0.75, 0.95])[["infection_prob", "DALYs pppy"]]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+str(ra.name)+"_summary.csv"

        #results_long.to_csv(path_or_buf=response, sep=',',float_format='%.2f', index=False, decimal=".")
        results_long.to_csv(path_or_buf=response, sep=',', decimal=".")
        
        return response
    else:
        return HttpResponseRedirect(reverse('login'))



# Modelling risk
@login_required(login_url="/login")
def calculate_risk(request, ra_id):
    ra = RiskAssessment.objects.get(id = ra_id)
    # Selecting inflow concentration based in source water type
    df_inflow = read_frame(Inflow.objects.filter(water_source=ra.source).values("min", "max", "pathogen__pathogen", "water_source__water_source_name"))
    df_inflow = df_inflow[df_inflow["pathogen__pathogen"].isin(["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"])]
    # Querying for Logremoval based on selected treatments
    df_treatment=read_frame(LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values("min", "max", "treatment__name", "pathogen_group__pathogen_group"))

    results_long = simulate_risk(ra)
    
    results_long["pathogen"] = results_long["variable"].str.split("_", expand=True)[0]
    results_long["stat"] = results_long["variable"].str.split("_", expand=True)[1]

    health = read_frame(Health.objects.all())
    results_long = pd.merge(results_long, health, on = "pathogen")
    results_long["DALYs pppy"] = results_long.value*results_long.infection_to_illness.astype(float)*results_long.dalys_per_case.astype(float)


    fig = px.box(results_long, 
             x="stat", 
             y="value", color="pathogen",
                            points="all",  
                            log_y =True, 
                            title="Risk as probability of infection per year",
                            color_discrete_sequence=["#75c3ff", "#007c9f", "#212c52"])

  
    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Risk assessment as probability of infection per year'},
        xaxis_title = "",
        yaxis_title = "Probability of infection per year",
        #markersize= 12,
        )
    fig.add_hline(y=0.0001, 
                    line_dash="dashdot",
                    line=dict(color="#007c9f", width = 3))
    fig.update_layout(legend=dict(
                 orientation="h",
                 yanchor="top",
                 #text= "Reference pathogen",
                 y=-.1,
                 xanchor="left",
                x=0),
                annotations=[go.Annotation(y = -4, x =1.2,
                        text = "Tolerable risk level of 1/10000 infections pppy",
                        bgcolor = "#007c9f",
                        bordercolor= "white",
                        borderpad = 5,
                        font = dict(color = "white"))])


   
    #fig.update_annotations(y = 0.0001, x = 1,  text = "Tolerable risk level")

    fig.update_traces(marker_size = 8)#['#75c3ff', "red"],#, marker_line_color='#212c52',

    
    risk_plot = plot(fig, output_type = "div")

    fig = px.box(results_long, 
             x="stat", 
             y="DALYs pppy", color="pathogen",
                            points="all",  
                            log_y =True, 
                            
                            color_discrete_sequence=["#75c3ff", "#007c9f", "#212c52"])

  
    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Risk in Disability adjusted life years (DALYs) per person per year (pppy)'},
        xaxis_title = "",
        yaxis_title = "DALYs pppy",
        annotations=[go.Annotation(y = -6, x = 1.2,
                        text = "Tolerable risk level of 1µDALY pppy",
                        bgcolor = "#007c9f",
                        bordercolor= "white",
                        borderpad = 5,
                        font = dict(color = "white"))]
        #markersize= 12,
        )
    
    fig.update_layout(legend=dict(
                 orientation="h",
                 yanchor="top",
                 #text= "Reference pathogen",
                 y=-.1,
                 xanchor="left",
                x=0))
    fig.add_hline(y=0.000001, 
                        line_dash="dashdot",
                        line=dict(color="#007c9f", width = 3))
                        #annotation_text="tolerable risk level")
                        #annotation_position = "top left",
                        #annotation=dict(font_size=20, font_family="Times New Roman"))
                        #annotation_position="bottom right")
    fig.update_traces(marker_size = 8)#['#75c3ff', "red"],#, marker_line_color='#212c52',

    
    daly_plot = plot(fig, output_type = "div")


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
            color_discrete_sequence=["#005269", "#007c9e", "#a3d1ec","#3494ae","#00B8eb"])

    fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], 
                            font = dict(size = 13, color = "black")))
    
    




    fig2.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Inflow concentrations of reference pathogens'},
        yaxis_title = "Source water concentraitons in N/L",
        )
       
    plot_div2 = plot(fig2, output_type = "div")

    # reshaping     
    df = pd.melt(df_treatment, ("treatment__name", "pathogen_group__pathogen_group"))
    df = df.rename(columns = {"treatment__name": "Treatment", "pathogen_group__pathogen_group": "Pathogen Group", "variable":""})
    fig = px.bar(df, x="", y = "value", 
    color="Treatment", facet_col="Pathogen Group",
    category_orders={"Pathogen Group": ["Viruses", "Bacteria", "Protozoa"]},
    color_discrete_sequence=["#005269", "#007c9e", "#a3d1ec","#3494ae","#00B8eb"])

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font = dict(size = 13)))
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
        title = {'text':'Treatment performance of selected treatments'},
        
        yaxis_title = "Logremoval of individual treatment step",
        )


    plot_div = plot(fig, output_type = "div")
    
   

    return render(request,"qmratool/results.html", {"plot_div":plot_div, 
    "plot_div2":plot_div2, 
    "daly_plot":daly_plot ,
    "risk_plot": risk_plot,
    "ra":ra
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



from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

@login_required(login_url="/login")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'qmratool/change_password.html', {
        'form': form
    })

from django.views.generic.edit import DeleteView

class UserDeleteView(DeleteView):
    # specify the model you want to use
    model = User
     
    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url ="/login"
     
    template_name = "qmratool/usermodel_confirm_delete.html"





@login_required(login_url="/login")
def api_treatments(request):
    treatments = Treatment.objects.filter(user__in = [request.user, 8])
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([treatment.serialize() for treatment in treatments], safe=False)

@login_required(login_url="/login")
def api_treatments_by_id(request, treatment_id):
    treatments = Treatment.objects.filter(id = treatment_id)
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([treatment.serialize() for treatment in treatments], safe=False)

@login_required(login_url="/login")
def api_sources_by_id(request, source_id):
    sources = SourceWater.objects.filter(id = source_id)
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([source.serialize() for source in sources], safe=False)

@login_required(login_url="/login")
def api_exposure_by_id(request, exposure_id):
    exposures = Exposure.objects.filter(id = exposure_id)
    # Filter emails returned based on mailbox
    
    # Return emails in reverse chronologial order
    return JsonResponse([exposure.serialize() for exposure in exposures], safe=False)


def annual_risk(nexposure, event_probs):
    return 1-np.prod(1-np.random.choice(event_probs, nexposure, True))


def simulate_risk(ra):
    # Selecting inflow concentration based in source water type
    df_inflow = read_frame(Inflow.objects.filter(water_source=ra.source).values("min", "max", "pathogen__pathogen", "water_source__water_source_name"))
    df_inflow = df_inflow[df_inflow["pathogen__pathogen"].isin(["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"])]
    # Querying dose response parameters based on pathogen inflow
    dr_models = read_frame(DoseResponse.objects.filter(pathogen__in=Pathogen.objects.filter(pathogen__in=df_inflow["pathogen__pathogen"])))

    # Querying for Logremoval based on selected treatments
    df_treatment=read_frame(LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values("min", "max", "treatment__name", "pathogen_group__pathogen_group"))
    
    # Summarizing treatment to treatment max and treatment min
    #df_treatment_summary=df_treatment.groupby(["pathogen_group__pathogen_group"]).sum().reset_index()
    df_treatment_summary=df_treatment.groupby(["pathogen_group__pathogen_group"])[["min", "max"]].apply(lambda x : x.sum()).reset_index()
    
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
                                                     high= df_treat["min"], 
                                                     size= 10000),
                            "LRVmax": np.random.uniform(low= df_treat["max"], 
                                                     high= df_treat["max"], 
                                                     size= 10000)})
        risk_df["outflow"]=risk_df["inflow"] - risk_df["LRV"]
        risk_df["outflow_min"]=risk_df["inflow"] - risk_df["LRVmax"]

        risk_df["dose"] = (10**risk_df["outflow"])*float(ra.exposure.volume_per_event)
        risk_df["dose_min"] = (10**risk_df["outflow_min"])*float(ra.exposure.volume_per_event)

        if selector != "Protozoa":
            risk_df["probs"] = 1 - (1 + (risk_df["dose"]) * (2 ** (1/float(dr.alpha)) - 1)/float(dr.n50)) ** -float(dr.alpha)
            risk_df["probs_min"] = 1 - (1 + (risk_df["dose_min"]) * (2 ** (1/float(dr.alpha)) - 1)/float(dr.n50)) ** -float(dr.alpha)

        else:
            risk_df["probs"] = 1 - np.exp(-float(dr.k)*(risk_df["dose"]))
            risk_df["probs_min"] = 1 - np.exp(-float(dr.k)*(risk_df["dose_min"]))

        results[row["pathogen__pathogen"]+"_MinimumLRV"] = [annual_risk(int(ra.exposure.events_per_year), risk_df["probs"] ) for _ in range(1000)]
        results[row["pathogen__pathogen"]+"_MaximumLRV"] = [annual_risk(int(ra.exposure.events_per_year), risk_df["probs_min"] ) for _ in range(1000)]

    results_long = pd.melt(results)
    results_long["log probability"] = np.log10(results_long["value"])
    return results_long