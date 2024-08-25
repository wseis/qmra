from django.urls import path
from qmra.treatment import views


urlpatterns = [
    path(
        "treatment",
        views.treatment_view,
        name="treatment",
    ),
    path(
        "treatment/<int:treatment_id>",
        views.treatment_view,
        name="treatment",
    )
]

