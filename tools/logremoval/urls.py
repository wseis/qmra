from django.urls import path
from . import views
from django.urls import path
from logremoval.views import ImportView


app_name = "logremoval"

urlpatterns = [
    path('', ImportView.as_view(), name = "import"),
]
