from typing import Protocol

from orders.models import Order


class OrderBroadcaster(Protocol):
    def broadcast(self, order: Order) -> None: ...
