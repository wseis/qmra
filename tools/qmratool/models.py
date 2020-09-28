from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    pass

class SourceWater(models.Model):
    name=models.CharField(max_length=64)
    description=models.CharField(max_length=2000)

class Treatment(models.Model):
    name = models.CharField(max_length=64)
    group=models.CharField(max_length=64)
    description=models.TextField(max_length=2000)
   
class Reference(models.Model):
    name=models.CharField(max_length=50)
    link=models.URLField(blank=True)

class LogRemoval(models.Model):
    min=models.DecimalField(    decimal_places=1, max_digits=4)
    max = models.DecimalField( decimal_places=1, max_digits=4)
    treatment=models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="logremoval")

class PathogenGroup(models.Model):
    pathogen_group=models.CharField(max_length=64)
    description=models.TextField(max_length=2000)

class Exposure(models.Model):
    use=models.CharField(max_length=50)
    description=models.CharField(max_length=64)
    events_per_year=models.IntegerField()
    volume_per_evenet=models.DecimalField( decimal_places=4, max_digits=10)

    
class RiskAssessment(models.Model):
    user=models.ForeignKey(User, on_delete=models.PROTECT, related_name="assessments")
    name=models.CharField(max_length=64, default="")
    description=models.TextField(max_length=2000, blank=True)
    source=models.ForeignKey(SourceWater, on_delete=models.PROTECT, default=1, blank = True)
    treatment=models.ManyToManyField(Treatment, related_name="treatment",default=1 ,   blank=True)
    exposure=models.ForeignKey(Exposure, on_delete=models.PROTECT, default=1 ,null=True)



