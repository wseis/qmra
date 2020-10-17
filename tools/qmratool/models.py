from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    pass

class SourceWater(models.Model):
    water_source_name=models.CharField(max_length=64)
    water_source_description=models.CharField(max_length=2000)

class Treatment(models.Model):
    name = models.CharField(max_length=64)
    group=models.CharField(max_length=64)
    description=models.TextField(max_length=2000)
   
class Reference(models.Model):
    name=models.CharField(max_length=50)
    link=models.URLField(blank=True)


class PathogenGroup(models.Model):
    pathogen_group=models.CharField(max_length=64)
    description=models.TextField(max_length=2000)

class Pathogen(models.Model):
    pathogen=models.CharField(max_length=64, default = "Rota")
    description=models.TextField(max_length=2000)
    pathogen_group=models.ForeignKey(PathogenGroup, on_delete=models.CASCADE, related_name="pathogens")

class LogRemoval(models.Model):
    reference=models.ForeignKey(Reference, related_name="logremoval", on_delete=models.CASCADE)
    pathogen_group=models.ForeignKey(PathogenGroup, on_delete=models.CASCADE, related_name="logremoval")
    min=models.DecimalField(    decimal_places=1, max_digits=4)
    max = models.DecimalField( decimal_places=1, max_digits=4)
    mean = models.DecimalField( decimal_places=3, max_digits=6, null = True)
    alpha = models.DecimalField( decimal_places=3, max_digits=6, null = True)
    beta = models.DecimalField( decimal_places=3, max_digits=6, null = True)
    distribution=models.CharField(default="uniform", max_length=64)
    treatment=models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="logremoval")

class Exposure(models.Model):
    use=models.CharField(max_length=250)
    description=models.CharField(max_length=2000)
    events_per_year=models.IntegerField(default = 10)
    volume_per_event=models.DecimalField( decimal_places=4, max_digits=10)
    reference=models.ForeignKey(Reference, on_delete=models.CASCADE)

    
class RiskAssessment(models.Model):
    user=models.ForeignKey(User, on_delete=models.PROTECT, related_name="assessments")
    name=models.CharField(max_length=64, default="")
    description=models.TextField(max_length=2000, blank=True)
    source=models.ForeignKey(SourceWater, on_delete=models.PROTECT, default=1, blank = True)
    treatment=models.ManyToManyField(Treatment, related_name="treatments",default=1 ,   blank=True)
    exposure=models.ManyToManyField(Exposure, default=1 ,null=True)



