from django.urls import path
from qmra.scenario import views


urlpatterns = [
    path(
        "scenario",
        views.exposure_scenario_view,
        name="scenario",
    ),
    path(
        "scenario/<int:scenario_id>",
        views.exposure_scenario_view,
        name="scenario",
    )
]