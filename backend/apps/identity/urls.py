from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LoginView, CurrentUserView


urlpatterns = [
    path(
        "auth/register/",
        RegisterView.as_view(),
        name="auth-register",
    ),
    path(
        "auth/login/",
        LoginView.as_view(),
        name="auth-login",
    ),
    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="auth-refresh",
    ),
    path(
        "users/me/",
        CurrentUserView.as_view(),
        name="user-me",
    ),
]