from typing import Iterable

import numpy as np

from qmra.risk_assessment.models import RiskAssessment, RiskAssessmentResult, Treatment, PathogenGroup, DefaultPathogens


def get_annual_risk(
        inflow_min: float, inflow_max: float,
        log_removal: float,
        volume_per_event: float,
        events_per_year: int,
        distribution,
        n_events: int = 10_000,
        n_years: int = 1000,
):
    inflow = np.random.normal(
        loc=(np.log10(inflow_min + 10 ** (-8)) + np.log10(inflow_max))/2,
        scale=(np.log10(inflow_max) - np.log10(inflow_min + 10 ** (-8)))/4,
        size=n_events
    )
    lrv = np.ones((n_events,)) * log_removal
    outflow = inflow - lrv
    dose = (10 ** outflow) * volume_per_event
    event_probs = distribution.pdf(dose)
    event_samples = np.random.choice(event_probs, size=(n_years, events_per_year), replace=True)
    return 1 - np.prod(1 - event_samples, axis=1)


def lrv_by_pathogen_group(treatments: Iterable[Treatment]) -> dict:
    lrvs = {
        PathogenGroup.Bacteria: dict(min=0, max=0),
        PathogenGroup.Viruses: dict(min=0, max=0),
        PathogenGroup.Protozoa: dict(min=0, max=0)
    }

    def zero_if_none(x): return x if x is not None else 0

    for t in treatments:
        lrvs[PathogenGroup.Bacteria]["min"] += zero_if_none(t.bacteria_min)
        lrvs[PathogenGroup.Bacteria]["max"] += zero_if_none(t.bacteria_max)
        lrvs[PathogenGroup.Viruses]["min"] += zero_if_none(t.viruses_min)
        lrvs[PathogenGroup.Viruses]["max"] += zero_if_none(t.viruses_max)
        lrvs[PathogenGroup.Protozoa]["min"] += zero_if_none(t.protozoa_min)
        lrvs[PathogenGroup.Protozoa]["max"] += zero_if_none(t.protozoa_max)
    return lrvs


def assess_risk(risk_assessment: RiskAssessment, inflows, treatments, save=True) -> dict[str, RiskAssessmentResult]:
    # assuming the model has been already validated
    lrvs = lrv_by_pathogen_group(treatments)
    results = {}

    for inflow in inflows:
        # unpack params
        pathogen = DefaultPathogens.get(inflow.pathogen)
        group = pathogen.group
        dist = pathogen.get_distribution()

        def to_dalys(pr, pat=pathogen):
            return pr * pat.infection_to_illness * pat.dalys_per_case

        # min / max probs
        min_prob = get_annual_risk(
            inflow.min, inflow.max,
            lrvs[group]["max"],
            risk_assessment.volume_per_event, risk_assessment.events_per_year,
            dist
        )
        max_prob = get_annual_risk(
            inflow.min, inflow.max,
            lrvs[group]["min"],
            risk_assessment.volume_per_event, risk_assessment.events_per_year,
            dist
        )
        # get the stats
        min_prob_mean = min_prob.mean()
        max_prob_mean = max_prob.mean()
        maximum_lrv_min = min_prob.min()
        maximum_lrv_max = min_prob.max()
        maximum_lrv_q1 = np.percentile(min_prob, 25)
        maximum_lrv_q3 = np.percentile(min_prob, 75)
        maximum_lrv_median = np.median(min_prob)
        minimum_lrv_min = max_prob.min()
        minimum_lrv_max = max_prob.max()
        minimum_lrv_q1 = np.percentile(max_prob, 25)
        minimum_lrv_q3 = np.percentile(max_prob, 75)
        minimum_lrv_median = np.median(max_prob)
        # make result
        results[inflow.pathogen] = RiskAssessmentResult(
            risk_assessment=risk_assessment,
            infection_risk=(min_prob_mean + max_prob_mean) > (10 ** -4),
            dalys_risk=to_dalys(min_prob_mean+max_prob_mean) > (10 ** -6),
            pathogen=inflow.pathogen,
            infection_maximum_lrv_min=maximum_lrv_min,
            infection_maximum_lrv_max=maximum_lrv_max,
            infection_maximum_lrv_q1=maximum_lrv_q1,
            infection_maximum_lrv_q3=maximum_lrv_q3,
            infection_maximum_lrv_median=maximum_lrv_median,
            infection_minimum_lrv_min=minimum_lrv_min,
            infection_minimum_lrv_max=minimum_lrv_max,
            infection_minimum_lrv_q1=minimum_lrv_q1,
            infection_minimum_lrv_q3=minimum_lrv_q3,
            infection_minimum_lrv_median=minimum_lrv_median,
            dalys_maximum_lrv_min=to_dalys(maximum_lrv_min),
            dalys_maximum_lrv_max=to_dalys(maximum_lrv_max),
            dalys_maximum_lrv_q1=to_dalys(maximum_lrv_q1),
            dalys_maximum_lrv_q3=to_dalys(maximum_lrv_q3),
            dalys_maximum_lrv_median=to_dalys(maximum_lrv_median),
            dalys_minimum_lrv_min=to_dalys(minimum_lrv_min),
            dalys_minimum_lrv_max=to_dalys(minimum_lrv_max),
            dalys_minimum_lrv_q1=to_dalys(minimum_lrv_q1),
            dalys_minimum_lrv_q3=to_dalys(minimum_lrv_q3),
            dalys_minimum_lrv_median=to_dalys(minimum_lrv_median),
        )
        if save:
            results[inflow.pathogen].save()
    return results
