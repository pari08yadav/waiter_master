from django.contrib.auth import authenticate


class DjangoCredentialAuthenticator:
    """Django auth adapter for credential verification."""

    def authenticate(self, request, username: str, password: str):
        return authenticate(request, username=username, password=password)
