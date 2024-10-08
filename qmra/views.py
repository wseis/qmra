from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
import django
from qmra.risk_assessment.models import RiskAssessment

from django.db import models


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("assessments"))
    else:
        return HttpResponseRedirect(reverse("login"))


def dsgvo(request):
    return render(request, "DSGVO.html")


def health(request):
    django.db.connection.ensure_connection()
    return HttpResponse("Ok")


def ready(request):
    django.db.connection.ensure_connection()
    return HttpResponse("Ok")