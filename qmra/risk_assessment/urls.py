from django.urls import path
from qmra.risk_assessment import views


urlpatterns = [
    path(
        "assessment",
        views.risk_assessment_view,
        name="assessment",
    ),
    path(
        "assessment/<int:risk_assessment_id>/result",
        views.calculate_risk,
        name="assessment-result",
    ),
    path(
        "assessment/<int:risk_assessment_id>/export",
        views.export_summary,
        name="assessment-export",
    ),
    path(
        "assessment/<int:risk_assessment_id>",
        views.risk_assessment_view,
        name="assessment",
    ),
    path(
        "comparison",
        views.comparison_view,
        name="comparison"
    ),
    path(
        "assessment/guided-form",
        views.RAFormWizard.as_view(),
        name="guided-form"
    )
]