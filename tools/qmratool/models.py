from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    pass

class SourceWater(models.Model):
    water_source_name=models.CharField(max_length=64)
    water_source_description=models.CharField(max_length=2000)
    def __str__(self):
      return self.water_source_name


class Treatment(models.Model):
    user = models.ForeignKey(User, related_name="treatments", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    group=models.CharField(max_length=64, default = "wastewater")
    description=models.TextField(max_length=250)
    #category = models.CharField(max_length=64, default = "wastewater")
    def __str__(self):
      return self.name
         
class Reference(models.Model):
    name=models.CharField(max_length=50)
    link=models.URLField(blank=True)
    def __str__(self):
      return self.name


class PathogenGroup(models.Model):
    pathogen_group=models.CharField(max_length=64)
    description=models.TextField(max_length=2000)
    def __str__(self):
      return self.pathogen_group

class Pathogen(models.Model):
    pathogen=models.CharField(max_length=64, default = "Rota")
    description=models.TextField(max_length=2000)
    pathogen_group=models.ForeignKey(PathogenGroup, on_delete=models.CASCADE, related_name="pathogens")
    def __str__(self):
      return self.pathogen

class LogRemoval(models.Model):
    reference=models.ForeignKey(Reference, related_name="logremoval",  default = 51, on_delete=models.CASCADE)
    pathogen_group=models.ForeignKey(PathogenGroup, on_delete=models.CASCADE, related_name="logremoval")
    min=models.DecimalField(    decimal_places=1, max_digits=4)
    max = models.DecimalField( decimal_places=1, max_digits=4)
    mean = models.DecimalField( decimal_places=3, max_digits=6, null = True)
    alpha = models.DecimalField( decimal_places=3, max_digits=6, null = True)
    beta = models.DecimalField( decimal_places=3, max_digits=6, null = True)
    distribution=models.CharField(default="uniform", max_length=64)
    treatment=models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="logremoval")
    #def __str__(self):
     # return self.treatment

class Inflow(models.Model):
    pathogen=models.ForeignKey(Pathogen, on_delete=models.CASCADE)
    reference=models.ForeignKey(Reference, on_delete=models.CASCADE)
    water_source= models.ForeignKey(SourceWater, on_delete=models.CASCADE)
    min=models.DecimalField( decimal_places=8, default = -100,max_digits=20)
    max = models.DecimalField( decimal_places=8,default = -100, max_digits=20)
    mean = models.DecimalField( decimal_places=8, max_digits=20, default = -100,null = True)
    alpha = models.DecimalField( decimal_places=8, max_digits=20,default = -100, null = True)
    beta = models.DecimalField( decimal_places=8, max_digits=20, default = -100, null = True)
    distribution=models.CharField(default="lognormal", max_length=64)
    pathogen_in_ref=models.CharField(max_length=200, default = "unknown")
    notes= models.CharField(max_length=200, default = "unknown")

class Health(models.Model):
    pathogen=models.ForeignKey(Pathogen, on_delete=models.CASCADE)
    reference=models.ForeignKey(Reference, on_delete=models.CASCADE)
    infection_to_illness=models.DecimalField( decimal_places=2, max_digits=3)	
    dalys_per_case=models.DecimalField(decimal_places=6, max_digits=6)

class DoseResponse(models.Model):
    pathogen=	models.ForeignKey(Pathogen, on_delete=models.CASCADE)
    bestfitmodel=models.CharField(max_length=250, default= "unknown")
    k	=models.DecimalField(decimal_places=10, default = 0, max_digits=20)
    alpha=	models.DecimalField(decimal_places=10,default = 0, max_digits=20)
    n50	=models.DecimalField(decimal_places=10,default = 0, max_digits=20)
    hosttype=	models.CharField(max_length=250, default= "unknown")
    doseunits=	models.CharField(max_length=250, default= "unknown")
    route=	models.CharField(max_length=250, default= "unknown")
    response=	models.CharField(max_length=250, default= "unknown")
    reference=models.ForeignKey(Reference, on_delete=models.CASCADE)




class Guideline(models.Model):
    name=models.CharField(max_length=250)
    description=models.CharField(max_length=250)
    reference=models.ForeignKey(Reference, on_delete=models.CASCADE, default = 40)



class Exposure(models.Model):
    user = models.ForeignKey(User, related_name="scenarios", on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250)
    events_per_year = models.IntegerField(default = 10)
    volume_per_event = models.DecimalField( decimal_places=4, max_digits=10)
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, default = 51)
    def __str__(self):
      return self.name
    
class RiskAssessment(models.Model):
    user=models.ForeignKey(User, on_delete=models.PROTECT, related_name="assessments")
    name=models.CharField(max_length=64, default="")
    description=models.TextField(max_length=500, blank=True)
    source=models.ForeignKey(SourceWater, on_delete=models.PROTECT, default=1,  blank = True)
    treatment=models.ManyToManyField(Treatment, related_name="treatments", default=1 ,  blank=True)
    exposure=models.ManyToManyField(Exposure, default=1 ,null=True,  blank = True)
    def __str__(self):
      return self.name



