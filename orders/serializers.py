from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from orders.models import Order, OrderItem
from restaurants.models import MenuItem, Table
from restaurants.serializers import LiteMenuItemSerializer, LiteTableSerializer, SerializedRelationField


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = SerializedRelationField("uid", MenuItem.objects.filter(available=True), LiteMenuItemSerializer)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["uid", "menu_item", "price", "total_price", "price_type", "quantity"]

    def validate(self, attrs):
        OrderItem(**attrs).clean()
        return super().validate(attrs)


class OrderSerializer(serializers.ModelSerializer):
    table = SerializedRelationField("uid", Table.objects, LiteTableSerializer)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["uid", "table", "total_price", "status", "status_display", "session_uid", "items"]

    def get_items(self, instance: Order):
        return OrderItemSerializer(instance=instance.orderitem_set.all(), many=True).data
