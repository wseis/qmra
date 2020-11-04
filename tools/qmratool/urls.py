from django.urls import path
from . import views
#from .views import TreatmentCreateView

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    #risk assessment creation urls
    path("new", views.new_assessment, name="new_assessment"),
    path("edit/<int:ra_id>", views.edit_assessment, name="edit_assessment"),
    path("delete/<int:ra_id>", views.delete_assessment, name="delete"),
    
    #scenario creation urls
    path('create_scenario', views.create_scenario, name='scenario_create'),
    path('edit_scenario', views.edit_scenario, name='scenario_edit'),
    path('delete_scenario/<int:scenario_id>', views.delete_scenario, name='scenario_delete'),
    
    # Treatment creation urls
    path('treatment_create', views.treatment_create, name='treatment_create'),
    path('source_create', views.source_create, name='source_create'),

    # Results
    path("results/<int:ra_id>", views.calculate_risk, name="results"),
]

