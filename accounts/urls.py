from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts.interfaces.http import views as account_views

api_router = DefaultRouter()
api_router.register("user", account_views.UserViewSet, basename="user")
api_router.register("user-profile", account_views.UserProfileViewSet, basename="user-profile")

urlpatterns = [
    path("login/", account_views.LoginView.as_view(), name="login"),
    path("logout/", account_views.LogoutView.as_view(), name="logout"),
]
