import enum
import json
import uuid

import numpy as np
from django.db import models
from django.db.models import QuerySet

from qmra.user.models import User
from itertools import groupby
from typing import Optional, Any
import abc
import dataclasses as dtc
from django.utils.functional import classproperty


class ExponentialDistribution:
    def __init__(self, k):
        self.k = k

    def pdf(self, x):
        return 1 - np.exp(-self.k * x)


class BetaPoissonDistribution:
    def __init__(self, alpha, n50):
        self.alpha = alpha
        self.n50 = n50

    def pdf(self, x):
        return 1 - (1 + x * (2 ** (1 / self.alpha) - 1) / self.n50) ** -self.alpha


class StaticEntity(metaclass=abc.ABCMeta):
    _raw_data: Optional[dict[str, dict[str, Any]]] = None

    @property
    @abc.abstractmethod
    def source(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def model(self) -> dtc.dataclass:
        pass

    @property
    @abc.abstractmethod
    def primary_key(self) -> str:
        pass

    @classproperty
    def raw_data(cls) -> dict[str, dict[str, Any]]:
        if cls._raw_data is None:
            with open(cls.source, "r") as f:
                cls._raw_data = json.load(f)
        return cls._raw_data

    @classproperty
    def data(cls) -> dict[str, model]:
        return {k: cls.model.from_dict(r) for k, r in cls.raw_data.items()}

    @classmethod
    @abc.abstractmethod
    def choices(cls):
        pass

    @classmethod
    def get(cls, pk: str):
        return cls.data[pk]


class PathogenGroup(models.TextChoices):
    Bacteria = "Bacteria"
    Viruses = "Viruses"
    Protozoa = "Protozoa"


class ModelDistributionType(enum.Enum):
    exponential = "exponential"
    beta_poisson = "beta-Poisson"


@dtc.dataclass
class DefaultPathogenModel:
    group: PathogenGroup
    name: str
    # fields from "doseResponse.csv"
    best_fit_model: ModelDistributionType
    k: Optional[float]
    alpha: Optional[float]
    n50: Optional[float]
    # fields from "health.csv"
    infection_to_illness: Optional[float] = None
    dalys_per_case: Optional[float] = None

    @classmethod
    def from_dict(cls, data) -> "DefaultPathogenModel":
        return DefaultPathogenModel(
            group=PathogenGroup(data["group"]),
            name=data["name"],
            best_fit_model=ModelDistributionType(data["best_fit_model"]),
            k=data["k"],
            alpha=data["alpha"],
            n50=data["n50"],
            infection_to_illness=data["infection_to_illness"],
            dalys_per_case=data["dalys_per_case"],
        )

    def get_distribution(self):
        if self.best_fit_model == ModelDistributionType.exponential:
            return ExponentialDistribution(self.k)
        elif self.best_fit_model == ModelDistributionType.beta_poisson:
            return BetaPoissonDistribution(self.alpha, self.n50)


class DefaultPathogens(StaticEntity):
    source = "qmra/static/data/default-pathogens.json"
    model = DefaultPathogenModel
    primary_key = "name"

    @classmethod
    def choices(cls):
        grouped = {grp.value: list(v) for grp, v in groupby(cls.data.values(), key=lambda x: x.group)}
        return [
            ("", "---------"),
            *[(grp, [(x.name, x.name) for x in v]) for grp, v in grouped.items()],
        ]


class Inflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risk_assessment = models.ForeignKey("RiskAssessment", related_name="inflows", on_delete=models.CASCADE)
    pathogen = models.CharField(choices=DefaultPathogens.choices(),
                                blank=False, null=False, max_length=256)
    # reference = models.ForeignKey(
    #     Reference, blank=True, null=True, default=None,
    #     on_delete=models.CASCADE)
    min = models.FloatField()
    max = models.FloatField()
    # pathogen_in_ref = models.CharField(max_length=200, default="unknown")
    # notes = models.CharField(max_length=200, default="unknown")


@dtc.dataclass
class DefaultInflowModel:
    pathogen_name: str
    source_name: str
    min: float
    max: float

    @classmethod
    def from_dict(cls, data: dict):
        return DefaultInflowModel(
            pathogen_name=data["pathogen_name"],
            source_name=data["source_name"],
            min=data["min"],
            max=data["max"]
        )


class DefaultInflows(StaticEntity):
    source = "qmra/static/data/default-inflows.json"
    model = DefaultInflowModel
    primary_key = None

    @classproperty
    def data(cls):
        return {k: [DefaultInflowModel.from_dict(d) for d in data]
                for k, data in cls.raw_data.items()}

    @classmethod
    def choices(cls):
        return []


@dtc.dataclass
class DefaultSourceModel:
    id: int
    name: str
    description: str
    inflows: list[DefaultInflowModel]

    @classmethod
    def from_dict(cls, data: dict):
        return DefaultSourceModel(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            inflows=DefaultInflows.get(data["name"])
        )


class DefaultSources(StaticEntity):
    source = "qmra/static/data/default-sources.json"
    model = DefaultSourceModel
    primary_key = "name"

    @classmethod
    def choices(cls):
        grouped = {grp: list(v) for grp, v in groupby(sorted(cls.data.values(), key=lambda x: x.name), key=lambda x: x.name.split(",")[0])}
        return [
            ("", "---------"),
            *[(k, [(x.name, x.name) for x in v]) for k, v in grouped.items()],
            ("other", "other")
        ]


@dtc.dataclass
class DefaultTreatmentModel:
    name: str
    group: str  # TextChoices?
    description: str
    bacteria_min: Optional[float]
    bacteria_max: Optional[float]
    viruses_min: Optional[float]
    viruses_max: Optional[float]
    protozoa_min: Optional[float]
    protozoa_max: Optional[float]

    @classmethod
    def from_dict(cls, data):
        return DefaultTreatmentModel(
            name=data['name'],
            group=data['group'],
            description=data['description'],
            bacteria_min=data['bacteria_min'],
            bacteria_max=data['bacteria_max'],
            viruses_min=data['viruses_min'],
            viruses_max=data['viruses_max'],
            protozoa_min=data['protozoa_min'],
            protozoa_max=data['protozoa_max'],
        )


class DefaultTreatments(StaticEntity):
    source = "qmra/static/data/default-treatments.json"
    model = DefaultTreatmentModel
    primary_key = "name"

    @classmethod
    def choices(cls):
        return [
            *[(x.name, x.name) for x in sorted(cls.data.values(), key=lambda x: x.name)],
        ]


class Treatment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risk_assessment = models.ForeignKey("RiskAssessment", related_name="treatments", on_delete=models.CASCADE)
    name = models.CharField(choices=DefaultTreatments.choices(), max_length=64)
    bacteria_min = models.FloatField(blank=True, null=True)
    bacteria_max = models.FloatField(blank=True, null=True)
    viruses_min = models.FloatField(blank=True, null=True)
    viruses_max = models.FloatField(blank=True, null=True)
    protozoa_min = models.FloatField(blank=True, null=True)
    protozoa_max = models.FloatField(blank=True, null=True)

    @classmethod
    def from_default(cls, default: DefaultTreatmentModel, risk_assessment):
        return Treatment.objects.create(
            risk_assessment=risk_assessment,
            name=default.name,
            bacteria_min=default.bacteria_min,
            bacteria_max=default.bacteria_max,
            viruses_min=default.viruses_min,
            viruses_max=default.viruses_max,
            protozoa_min=default.protozoa_min,
            protozoa_max=default.protozoa_max,
        )


@dtc.dataclass
class DefaultExposureModel:
    name: str
    description: str
    events_per_year: int
    volume_per_event: float

    @classmethod
    def from_dict(cls, data):
        return DefaultExposureModel(
            name=data["name"],
            description=data["description"],
            events_per_year=data["events_per_year"],
            volume_per_event=data["volume_per_event"],
        )


class DefaultExposures(StaticEntity):
    source = "qmra/static/data/default-exposures.json"
    model = DefaultExposureModel
    primary_key = "name"

    @classmethod
    def choices(cls):
        grouped = {grp: list(v) for grp, v in groupby(sorted(cls.data.values(), key=lambda x: x.name), key=lambda x: x.name.split(",")[0])}
        return [
            ("", "---------"),
            *[(k, [(x.name, x.name) for x in sorted(v, key=lambda x: x.name)]) for k, v in grouped.items()],
            ("other", "other")
        ]


class RiskAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="risk_assessments")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    name = models.CharField(max_length=64, default="", blank=True)
    description = models.TextField(max_length=500, default="", blank=True)
    source_name = models.CharField(
        choices=DefaultSources.choices(), blank=True, max_length=256
    )
    inflows: QuerySet[Inflow]
    treatments: QuerySet[Treatment]
    exposure_name = models.CharField(choices=DefaultExposures.choices(),
                                     blank=True, max_length=256)
    events_per_year = models.IntegerField()
    volume_per_event = models.FloatField()

    results: QuerySet["RiskAssessmentResult"]

    @property
    def infection_risk(self):
        return any(r.infection_risk for r in self.results.all())

    @property
    def dalys_risk(self):
        return any(r.dalys_risk for r in self.results.all())

    @property
    def pathogens_labels(self):
        return ", ".join([inflow.pathogen for inflow in self.inflows.all()])

    @property
    def treatments_labels(self):
        return ", ".join([treatment.name for treatment in self.treatments.all()])

    def __str__(self):
        return self.name


class RiskAssessmentResult(models.Model):
    risk_assessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, related_name="results")

    pathogen = models.CharField(choices=DefaultPathogens.choices(), max_length=256)

    infection_risk = models.BooleanField()
    dalys_risk = models.BooleanField()

    infection_minimum_lrv_min = models.FloatField()
    infection_minimum_lrv_max = models.FloatField()
    infection_minimum_lrv_q1 = models.FloatField()
    infection_minimum_lrv_q3 = models.FloatField()
    infection_minimum_lrv_median = models.FloatField()
    infection_maximum_lrv_min = models.FloatField()
    infection_maximum_lrv_max = models.FloatField()
    infection_maximum_lrv_q1 = models.FloatField()
    infection_maximum_lrv_q3 = models.FloatField()
    infection_maximum_lrv_median = models.FloatField()

    dalys_minimum_lrv_min = models.FloatField()
    dalys_minimum_lrv_max = models.FloatField()
    dalys_minimum_lrv_q1 = models.FloatField()
    dalys_minimum_lrv_q3 = models.FloatField()
    dalys_minimum_lrv_median = models.FloatField()
    dalys_maximum_lrv_min = models.FloatField()
    dalys_maximum_lrv_max = models.FloatField()
    dalys_maximum_lrv_q1 = models.FloatField()
    dalys_maximum_lrv_q3 = models.FloatField()
    dalys_maximum_lrv_median = models.FloatField()
