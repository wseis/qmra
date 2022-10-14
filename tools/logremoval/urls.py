from django.urls import path
from . import views
from django.urls import path
from logremoval.views import ImportView


app_name = "logremoval"

urlpatterns = [
    path('', ImportView.as_view(), name = "import"),
]
#from django.conf.urls import url
#from myproject.accounts import views


#from .views import TreatmentCreateView

#urlpatterns = [
 #   path("", views.index, name="index"),
    
#]
