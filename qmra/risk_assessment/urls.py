from django.urls import path
from qmra.risk_assessment import views


urlpatterns = [
    path(
        "assessments",
        views.list_risk_assessment_view,
        name="assessments",
    ),
    path(
        "assessment",
        views.risk_assessment_view,
        name="assessment",
    ),
    path(
        "assessment/<uuid:risk_assessment_id>",
        views.risk_assessment_view,
        name="assessment",
    ),
    path(
        "assessment/<uuid:risk_assessment_id>/results",
        views.risk_assessment_result,
        name="assessment-result",
    ),
    path(
        "assessment/results",
        views.risk_assessment_result,
        name="assessment-result",
    ),
    path(
        "inflows-plot",
        views.inflows_plots_view,
        name="inflows-plot",
    ),
    path(
        "treatments-plot",
        views.treatments_plots_view,
        name="treatments-plot",
    ),
    # path(
    #     "assessment/<int:risk_assessment_id>/export",
    #     views.export_summary,
    #     name="assessment-export",
    # ),
    # path(
    #     "assessment/<int:risk_assessment_id>",
    #     views.risk_assessment_view,
    #     name="assessment",
    # ),
    # path(
    #     "comparison",
    #     views.comparison_view,
    #     name="comparison"
    # ),
    # path(
    #     "assessment/guided-form",
    #     views.RAFormWizard.as_view(),
    #     name="guided-form"
    # )
]