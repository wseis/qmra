from django.db import models

from qmra.user.models import User
from qmra.scenario.models import ExposureScenario
from qmra.source.models import WaterSource
from qmra.treatment.models import Treatment, Pathogen, Reference


class RiskAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessments")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    name = models.CharField(max_length=64, default="")
    description = models.TextField(max_length=500, blank=True)
    source = models.ForeignKey(
        WaterSource, on_delete=models.PROTECT, default=1, blank=True
    )
    treatment = models.ManyToManyField(
        Treatment, related_name="treatments", default=1, blank=True
    )
    exposure = models.ForeignKey(
        ExposureScenario, default=1, null=True, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return self.name


class Comparison(models.Model):
    risk_assessment = models.ManyToManyField(RiskAssessment, blank=True)


class Health(models.Model):
    pathogen = models.ForeignKey(Pathogen, on_delete=models.CASCADE)
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    infection_to_illness = models.FloatField()
    dalys_per_case = models.FloatField()

    def __str__(self):
        return self.pathogen.pathogen


class DoseResponse(models.Model):
    pathogen = models.ForeignKey(Pathogen, on_delete=models.CASCADE)
    bestfitmodel = models.CharField(max_length=250, default="unknown")
    k = models.FloatField(default=0)
    alpha = models.FloatField(default=0)
    n50 = models.FloatField(default=0)
    hosttype = models.CharField(max_length=250, default="unknown")
    doseunits = models.CharField(max_length=250, default="unknown")
    route = models.CharField(max_length=250, default="unknown")
    response = models.CharField(max_length=250, default="unknown")
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
