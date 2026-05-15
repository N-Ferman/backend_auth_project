from django.urls import path

from apps.accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
)


urlpatterns = [
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),

    path("api/me/", MeView.as_view()),
]
