from django.urls import path
from . import views

#from django.conf.urls import url
#from myproject.accounts import views


#from .views import TreatmentCreateView

urlpatterns = [
    path("", views.index, name="index"),
    
]
