from django.contrib import admin
from django.urls import include, path
from qmra import views

urlpatterns = [
    path("", views.index, name="index"),
    path("health", views.health, name="health"),
    path("ready", views.ready, name="ready"),
    path("dsgvo", views.dsgvo, name="dsgvo"),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', include('qmra.risk_assessment.urls')),
    path('', include('qmra.user.urls')),
]
