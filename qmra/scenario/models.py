from django.db import models

from qmra.user.models import User
from qmra.treatment.models import Reference


class ExposureScenario(models.Model):
    user = models.ForeignKey(
        User, related_name="scenarios",
        blank=True, null=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250)
    events_per_year = models.IntegerField(default=10)
    volume_per_event = models.FloatField()
    reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        default=None, blank=True, null=True)

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "events_per_year": self.events_per_year,
            "volume_per_event": self.volume_per_event,
        }
