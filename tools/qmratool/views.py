from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from .forms import RAForm, SourceWaterForm, TreatmentForm, ExposureForm
from .models import *
from django.views.decorators.csrf import ensure_csrf_cookie
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
            assessment.save()
            #return HttpResponse(assessment.name)    
            return HttpResponseRedirect(reverse('source', args=(assessment.name,)))
        else:
            return HttpResponse(request, "Form not valid")
    else:
        form = RAForm()
    return render(request, 'qmratool/new_ra.html', {"form":form})

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


def use(request):
    uses = Exposure.objects.all()
    return render(request, "qmratool/use.html", {"uses":uses})


def summary(request):
    return render(request, "qmratool/summary.html")


def results(request):
    return render(request, "qmratool/results.html")





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
    return HttpResponseRedirect(reverse("index"))


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
