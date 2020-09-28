from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from .forms import RAForm
# Create your views here.


def index(request):
    return render(request, "qmratool/layout.html")

def new_assessment(request):
    form = RAForm()
    return render(request, 'qmratool/new_ra.html', {"form":form})

def source(request):
    return render(request, "qmratool/source.html")

def treatment(request):
    return render(request, "qmratool/treatment.html")


def use(request):
    return render(request, "qmratool/use.html")


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
