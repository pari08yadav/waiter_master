import json
import uuid
from dataclasses import dataclass
from urllib.parse import unquote

from django.shortcuts import get_object_or_404

from shared.common.taxonomies import OrderStatus
from orders.domain.ports import OrderBroadcaster
from orders.infrastructure.realtime.channel_order_broadcaster import (
    ChannelOrderBroadcaster,
)
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer
from restaurants.models import MenuItem, Table
from restaurants.serializers import TableSerializer


@dataclass
class OrderSummary:
    table: dict
    orders: list
    session_uid: str
    total_price: float


class OrderService:
    """Application service for table ordering workflows."""

    @staticmethod
    def ensure_session_uid(request) -> str:
        session_uid = request.session.get("uid")
        if not session_uid:
            session_uid = str(uuid.uuid4())
            request.session["uid"] = session_uid
        return session_uid

    @staticmethod
    def get_order_summary(table_uid: str, request) -> OrderSummary:
        table = get_object_or_404(Table, uid=table_uid)
        session_uid = OrderService.ensure_session_uid(request)
        orders = Order.objects.filter(
            table=table, session_uid=session_uid
        ).prefetch_related("orderitem_set__menu_item")

        return OrderSummary(
            table=TableSerializer(instance=table).data,
            orders=OrderSerializer(instance=orders, many=True).data,
            session_uid=session_uid,
            total_price=sum(order.total_price for order in orders),
        )

    @staticmethod
    def place_order_from_cookie(table_uid: str, request) -> Order:
        table = get_object_or_404(Table, uid=table_uid)
        session_uid = OrderService.ensure_session_uid(request)

        cart_cookie = request.COOKIES.get("cart")
        if not cart_cookie:
            raise ValueError("Cart is empty")

        cart = json.loads(unquote(cart_cookie))
        if not cart:
            raise ValueError("Cart is empty")

        order, _ = Order.objects.get_or_create(
            table=table, status=OrderStatus.PENDING, session_uid=session_uid
        )

        for key, val in cart.items():
            try:
                menu_uid, price_type = key.split("/", 1)
            except ValueError:
                continue

            menu_item = MenuItem.objects.filter(uid=menu_uid, available=True).first()
            if not menu_item:
                continue

            quantity = val.get("quantity", 0)
            if quantity <= 0:
                continue

            item, created = OrderItem.objects.get_or_create(
                order=order,
                menu_item=menu_item,
                price_type=price_type,
                defaults={"quantity": quantity},
            )
            if not created:
                item.quantity += quantity
            item.full_clean()
            item.save()

        return order

    @staticmethod
    def broadcast_order_update(
        order: Order, broadcaster: OrderBroadcaster | None = None
    ) -> None:
        gateway = broadcaster or ChannelOrderBroadcaster()
        gateway.broadcast(order)
