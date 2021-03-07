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
    path('treatment_edit', views.treatment_edit, name='treatment_edit'),
    path('treatment_delete/<int:treatment_id>', views.treatment_delete, name='treatment_delete'),
    path('LRV_edit/<int:treatment_id>/<int:pathogen_group_id>', views.LRV_edit, name = 'LRV_edit'),
    path('source_create', views.source_create, name='source_create'),

       
    # Results
    path("results/<int:ra_id>", views.calculate_risk, name="results"),
    path("bayes", views.bayes, name="bayes"),
    path("comparisons", views.comparison, name = "comparison"),

     # API Routes
    path("api_treatments", views.api_treatments, name="api_treatments"),
    path("api_treatments/<int:treatment_id>", views.api_treatments_by_id, name="api_treatments_by_id"),
    path("api_sources/<int:source_id>", views.api_sources_by_id, name="api_sources_by_id"),
    path("api_exposures/<int:exposure_id>", views.api_exposure_by_id, name="api_exposure_by_id"),
    
    #path("emails/<int:email_id>", views.email, name="email"),
    #path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
]

