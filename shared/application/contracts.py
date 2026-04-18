from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class AppResult(Generic[T]):
    """Simple, explicit result envelope for service boundaries."""

    ok: bool
    data: T | None = None
    error: str = ""
