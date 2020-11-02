from django.urls import path
from . import views
from .views import TreatmentCreateView

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_assessment, name="new_assessment"),
    path("edit/<int:ra_id>", views.edit_assessment, name="edit_assessment"),
    path("delete/<int:ra_id>", views.delete_assessment, name="delete"),
    path('create_treatment', TreatmentCreateView.as_view(), name='treatment_create'),
    path('create_scenario', views.create_scenario, name='scenario_create'),
    
    path("source/<str:ra_name>", views.source, name="source"),
    path("treatment/<int:ra_id>", views.treatment, name="treatment"),
     path("results/<int:ra_id>", views.calculate_risk, name="results"),
]

