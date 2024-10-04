"""test computation of risk assessment"""
from django.test import TestCase
from assertpy import assert_that

from qmra.risk_assessment.models import RiskAssessment, Inflow, Treatment, DefaultTreatments, RiskAssessmentResult, \
    DefaultPathogens
from qmra.risk_assessment.risk import assess_risk
from qmra.user.models import User


class TestAssesRisk(TestCase):
    def test_with_standard_pathogens_and_all_treatments(self):
        given_user = User.objects.create_user("test-user", "test-user@test.com", "password")
        given_user.save()
        given_ra = RiskAssessment.objects.create(
            user=given_user,
            events_per_year=1,
            volume_per_event=2,
        )
        given_ra.save()
        given_inflows = [
            Inflow.objects.create(
                risk_assessment=given_ra,
                pathogen="Rotavirus",
                min=0.1, max=0.2
            ),
            Inflow.objects.create(
                risk_assessment=given_ra,
                pathogen="Campylobacter jejuni",
                min=0.1, max=0.2
            ),
            Inflow(
                risk_assessment=given_ra,
                pathogen="Cryptosporidium parvum",
                min=0.1, max=0.2
            ),
        ]
        given_treatments = [
            Treatment.from_default(t, given_ra)
            for _, t in DefaultTreatments.data.items()
        ]
        given_ra.inflows.set(given_inflows, bulk=False)
        given_ra.treatments.set(given_treatments, bulk=False)

        results = assess_risk(given_ra)

        assert_that(len(results)).is_equal_to(len(given_inflows))

        assert_that(sorted([infl.pathogen for infl in given_inflows])).is_equal_to(
            sorted(results.keys())
        )

    def test_with_all_pathogens(self):
        given_user = User.objects.create_user("test-user", "test-user@test.com", "password")
        given_user.save()
        given_ra = RiskAssessment.objects.create(
            user=given_user,
            events_per_year=1,
            volume_per_event=2,
        )
        given_ra.save()
        given_inflows = [
            Inflow.objects.create(
                risk_assessment=given_ra,
                pathogen=p,
                min=0.1, max=0.2
            ) for p, _ in DefaultPathogens.data.items()
        ]
        given_treatments = [
            Treatment.from_default(DefaultTreatments.get("Conventional clarification"), given_ra),
            Treatment.from_default(DefaultTreatments.get("Dissolved air flotation"), given_ra),
        ]
        given_ra.inflows.set(given_inflows, bulk=False)
        given_ra.treatments.set(given_treatments, bulk=False)

        results = assess_risk(given_ra)

        assert_that(len(results)).is_equal_to(len(given_inflows))

        assert_that(sorted([infl.pathogen for infl in given_inflows])).is_equal_to(
            sorted(results.keys())
        )

    def test_regression_test(self):
        assert_that(False).is_true()