from django.contrib import admin
from django.urls import include, path
from qmra import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dsgvo", views.dsgvo, name="dsgvo"),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', include('qmra.risk_assessment.urls')),
    path('', include('qmra.treatment.urls')),
    path('', include('qmra.source.urls')),
    path('', include('qmra.scenario.urls')),
    path('', include('qmra.user.urls')),
]
