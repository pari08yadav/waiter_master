import uuid

from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView
from loguru import logger
from rest_framework.viewsets import ModelViewSet

from accounts.application.services.auth_service import AuthService
from accounts.forms import LoginForm
from accounts.models import UserProfile
from accounts.serializers import LiteUserProfileSerializer, UserProfileSerializer
from shared.common.mixins import AuthMixin


def is_ajax(request) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


class LoginView(FormView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy("common:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: LoginForm):
        user = AuthService.resolve_login_user(
            request=self.request,
            is_guest=form.cleaned_data.get("is_guest"),
            username=form.cleaned_data.get("username", ""),
            password=form.cleaned_data.get("password", ""),
        )
        if not user:
            form.errors.password = ("Invalid login credentials!!",)
            return self.form_invalid(form)
        login(self.request, user)
        return redirect(self.success_url)

    def form_invalid(self, form):
        if is_ajax(self.request):
            return JsonResponse({"status": 400, "errors": form.errors}, status=400)
        return super().form_invalid(form)


class LogoutView(AuthMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse("common:home"))


class UserProfileViewSet(AuthMixin, ModelViewSet):
    lookup_field = "uid"
    serializer_class = LiteUserProfileSerializer
    http_method_names = ("get", "patch")

    def get_queryset(self):
        return UserProfile.objects.all()


class UserViewSet(ModelViewSet):
    serializer_class = UserProfileSerializer
    http_method_names = ("get", "patch")

    def get_queryset(self):
        if self.request.method.upper() == "PATCH" and self.kwargs.get("uid"):
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.all()

    def get_object(self):
        if self.request.user.is_authenticated:
            return UserProfile.objects.get(user=self.request.user)
        uid = self.request.session.get("uid", str(uuid.uuid4()))
        self.request.session["uid"] = uid
        return UserProfile(uid=uid)
