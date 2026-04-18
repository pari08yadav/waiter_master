from typing import Protocol


class CredentialAuthenticator(Protocol):
    def authenticate(self, request, username: str, password: str): ...
