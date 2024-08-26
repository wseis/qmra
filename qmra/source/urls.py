from django.urls import path
from qmra.source import views


urlpatterns = [
    path(
        "source",
        views.source_view,
        name="source",
    ),
    path(
        "source/<int:source_id>",
        views.source_view,
        name="source",
    )
]