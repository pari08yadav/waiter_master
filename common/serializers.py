"""Compatibility facade for legacy common.serializers imports."""

from accounts.serializers import (
    ChainSerializer,
    LiteUserProfileSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from orders.serializers import OrderItemSerializer, OrderSerializer
from rest_framework import serializers
from restaurants.serializers import (
    CategorySerializer,
    LiteCategorySerializer,
    LiteMenuItemSerializer,
    LiteTableSerializer,
    MenuItemSerializer,
    RestaurantSerializer,
    SerializedRelationField,
    TableSerializer,
)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


__all__ = [
    "SerializedRelationField",
    "LoginSerializer",
    "UserSerializer",
    "ChainSerializer",
    "UserProfileSerializer",
    "LiteUserProfileSerializer",
    "RestaurantSerializer",
    "TableSerializer",
    "LiteTableSerializer",
    "CategorySerializer",
    "LiteCategorySerializer",
    "MenuItemSerializer",
    "LiteMenuItemSerializer",
    "OrderSerializer",
    "OrderItemSerializer",
]
