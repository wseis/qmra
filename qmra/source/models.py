from django.db import models

from qmra.user.models import User
from qmra.treatment.models import Pathogen, Reference


# Create your models here.
class WaterSource(models.Model):
    user = models.ForeignKey(
        User, related_name="water_sources",
        default=None, blank=True, null=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=2000)

    def __str__(self):
        return self.name
    
    def get_inflow(self, pathogen_group):
        try:
            return self.inflow.filter(pathogen__pathogen_group__pathogen_group=pathogen_group).first()
        except self.inflow.model.DoesNotExist:
            return None

    def serialize(self):
        def get_min_max(pathogen_group):
            inflow = self.get_inflow(pathogen_group)
            if inflow is not None:
                return float(inflow.min), float(inflow.max)
            else:
                return 'n.a.', 'n. a.'

        virus_min, virus_max = get_min_max("Viruses")
        bacteria_min, bacteria_max = get_min_max("Bacteria")
        protozoa_min, protozoa_max = get_min_max("Protozoa")
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "virus_min": virus_min,
            "virus_max": virus_max,
            "bacteria_min": bacteria_min,
            "bacteria_max": bacteria_max,
            "protozoa_min": protozoa_min,
            "protozoa_max": protozoa_max,
        }


class Inflow(models.Model):
    pathogen = models.ForeignKey(Pathogen, on_delete=models.CASCADE)
    reference = models.ForeignKey(
        Reference, blank=True, null=True, default=None,
        on_delete=models.CASCADE)
    water_source = models.ForeignKey(
        WaterSource,
        on_delete=models.CASCADE, related_name="inflow")
    min = models.FloatField(default=0)
    max = models.FloatField(default=1)
    mean = models.FloatField(null=True)
    alpha = models.FloatField(null=True)
    beta = models.FloatField(null=True)
    distribution = models.CharField(default="lognormal", max_length=64)
    pathogen_in_ref = models.CharField(max_length=200, default="unknown")
    notes = models.CharField(max_length=200, default="unknown")
