import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from django.db import transaction
from django.shortcuts import get_object_or_404
from loguru import logger

from orders.models import Order
from orders.serializers import OrderSerializer
from restaurants.models import Restaurant


@database_sync_to_async
def get_queryset(scope):
    user = scope["user"]
    if user.is_authenticated:
        return Restaurant.objects.filter(chain=user.userprofile.chain)
    return Restaurant.objects.none()


class QueryAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["queryset"] = await get_queryset(scope)
        return await self.app(scope, receive, send)


class OrderConsumer(WebsocketConsumer):
    def connect(self):
        chat_room = self.scope["session"].get("uid", None)
        if uid := self.scope["url_route"]["kwargs"].get("uid"):
            if self.scope["queryset"].filter(uid=uid).first():
                chat_room = str(uid)
        self.chat_room = chat_room
        logger.info(f"Connected to {chat_room}")
        async_to_sync(self.channel_layer.group_add)(self.chat_room, self.channel_name)
        self.accept()

    def websocket_disconnect(self, message):
        return super().websocket_disconnect(message)

    def receive(self, text_data):
        data = json.loads(text_data)
        instance = get_object_or_404(Order, uid=data.get("uid"))
        instance.status = data.get("status", instance.status)
        instance.clean()
        instance.save()

        channel_layer = self.channel_layer
        session_uid = str(instance.session_uid)
        restaurant_uid = str(instance.table.restaurant.uid)
        order_id = instance.pk

        def push_ws():
            o = Order.objects.get(pk=order_id)
            async_to_sync(channel_layer.group_send)(session_uid, {"type": "send_order", "order": o})
            async_to_sync(channel_layer.group_send)(restaurant_uid, {"type": "send_order", "order": o})

        transaction.on_commit(push_ws)

    def send_order(self, event):
        self.send(text_data=json.dumps(OrderSerializer(instance=event["order"]).data))
