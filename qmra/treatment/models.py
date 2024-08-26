from django.db import models

from qmra.user.models import User


class Treatment(models.Model):
    user = models.ForeignKey(
        User, related_name="treatments",
        default=None, blank=True, null=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64)
    group = models.CharField(max_length=64, default="wastewater")
    category = models.CharField(
        max_length=64,
        choices=[
            ("wastewater", "wastewater"),
            ("drinking_water", "drinking water"),
            ("surface_water", "surface water"),
        ],
        default="wastewater",
    )
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

    def get_lrv(self, pathogen_group):
        try:
            return self.logremoval.get(pathogen_group__pathogen_group=pathogen_group)
        except self.logremoval.model.DoesNotExist:
            return None

    def serialize(self):
        def get_min_max(pathogen_group):
            lrv = self.get_lrv(pathogen_group)
            if lrv is not None:
                return float(lrv.min), float(lrv.max)
            else:
                return 'n.a.', 'n. a.'

        virus_min, virus_max = get_min_max("Viruses")
        bacteria_min, bacteria_max = get_min_max("Bacteria")
        protozoa_min, protozoa_max = get_min_max("Protozoa")

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "group": self.group,
            "virus_min": virus_min,
            "virus_max": virus_max,
            "bacteria_min": bacteria_min,
            "bacteria_max": bacteria_max,
            "protozoa_min": protozoa_min,
            "protozoa_max": protozoa_max,
        }


class Reference(models.Model):
    name = models.CharField(max_length=128)
    link = models.URLField(blank=True, max_length=512)

    def __str__(self):
        return self.name


class PathogenGroup(models.Model):
    pathogen_group = models.CharField(max_length=64)
    description = models.TextField(max_length=2000)

    def __str__(self):
        return self.pathogen_group


class Pathogen(models.Model):
    name = models.CharField(max_length=64, default="Rota")
    description = models.TextField(max_length=2000, null=True, blank=True)
    pathogen_group = models.ForeignKey(
        PathogenGroup,
        on_delete=models.CASCADE, related_name="pathogens"
    )

    def __str__(self):
        return self.name


class LogRemoval(models.Model):
    reference = models.ForeignKey(
        Reference, related_name="logremoval", default=None, on_delete=models.CASCADE,
        null=True, blank=True
    )
    pathogen_group = models.ForeignKey(
        PathogenGroup, on_delete=models.CASCADE, related_name="logremoval"
    )
    min = models.FloatField()
    max = models.FloatField()
    mean = models.FloatField(null=True)
    alpha = models.FloatField(null=True)
    beta = models.FloatField(null=True)
    distribution = models.CharField(default="uniform", max_length=64)
    treatment = models.ForeignKey(
        Treatment, on_delete=models.CASCADE, related_name="logremoval"
    )
