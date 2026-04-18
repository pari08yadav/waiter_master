from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from orders.models import Order


class ChannelOrderBroadcaster:
    """Channels-based broadcast adapter."""

    def broadcast(self, order: Order) -> None:
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        async_to_sync(channel_layer.group_send)(
            str(order.session_uid), {"type": "send_order", "order": order}
        )
        async_to_sync(channel_layer.group_send)(
            str(order.table.restaurant.uid), {"type": "send_order", "order": order}
        )
