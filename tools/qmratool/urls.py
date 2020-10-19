from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_assessment, name="new_assessment"),
    path("source/<str:ra_name>", views.source, name="source"),
    path("treatment(<int:ra_id>", views.treatment, name="treatment"),
   
    path("results/<int:ra_id>", views.calculate_risk, name="results"),
]