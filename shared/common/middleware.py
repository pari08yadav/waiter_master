import pytz
from django.utils import timezone
from django.utils.timezone import activate

EXCLUDED_ROUTES = ("/login/", "/logout/")


class PatchRequestMiddleware:
    """Adds request.profile and request.chain mappings on authenticated requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if not request.path.startswith(EXCLUDED_ROUTES):
            if user.is_authenticated and hasattr(user, "userprofile"):
                request.profile = user.userprofile
                request.chain = user.userprofile.chain
        return self.get_response(request)


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(self.process_request(request))
        return response

    def process_request(self, request):
        if not request.path.startswith("/wtr-adm"):
            return request
        if request.user.is_authenticated:
            activate(pytz.timezone("Asia/Kolkata"))
        else:
            timezone.deactivate()
        return request
