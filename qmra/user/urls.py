from django.urls import path
import qmra.user.views as views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("password", views.change_password, name="change_password"),
    path("unregister/<pk>", views.UserDeleteView.as_view(), name="delete_user"),
]
