from django.contrib.auth.models import User

from accounts.models import Chain, UserProfile
from accounts.domain.ports import CredentialAuthenticator
from accounts.infrastructure.django_authenticator import DjangoCredentialAuthenticator
from shared.common.model_helpers import generate_chain_name, generate_username


class AuthService:
    """Application service for authentication use-cases."""

    @staticmethod
    def resolve_login_user(
        *,
        request,
        is_guest: bool,
        username: str = "",
        password: str = "",
        authenticator: CredentialAuthenticator | None = None,
    ):
        if is_guest:
            user = User.objects.create(username=generate_username())
            chain, _ = Chain.objects.get_or_create(name=generate_chain_name())
            UserProfile.objects.create(user=user, chain=chain, is_guest=True)
            return user
        provider = authenticator or DjangoCredentialAuthenticator()
        return provider.authenticate(request, username=username, password=password)
