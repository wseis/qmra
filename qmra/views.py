from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render

from qmra.risk_assessment.models import RiskAssessment


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("assessments"))
    else:
        return HttpResponseRedirect(reverse("login"))


def dsgvo(request):
    return render(request, "DSGVO.html")
