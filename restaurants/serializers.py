from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from restaurants.models import Category, MenuItem, Restaurant, Table


class SerializedRelationField(serializers.Field):
    def __init__(self, lookup_key: str, queryset: QuerySet, repr_serializer, **kwargs):
        self.lookup_key = lookup_key
        self.queryset = queryset
        self.repr_serializer = repr_serializer
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            value = data
            if isinstance(data, dict):
                key = self.lookup_key.split("__")[-1]
                value = data[key]
            if value:
                return self.queryset.get(**{self.lookup_key: value})
        except Exception as exc:
            raise ValidationError(exc)
        return None

    def to_representation(self, value):
        return self.repr_serializer(instance=value, context=self.context).data


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["uid", "name", "table_count", "category_count", "created", "updated"]


class LiteTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["uid", "number", "qr_code"]


class TableSerializer(serializers.ModelSerializer):
    restaurant = SerializedRelationField("uid", Restaurant.objects, RestaurantSerializer)
    number = serializers.IntegerField(required=False, allow_null=True)
    qr_code = serializers.ImageField(read_only=True)

    class Meta:
        model = Table
        fields = ["uid", "number", "restaurant", "qr_code", "created", "updated"]


class LiteCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["uid", "name"]


class CategorySerializer(serializers.ModelSerializer):
    restaurant = SerializedRelationField("uid", Restaurant.objects, RestaurantSerializer)

    class Meta:
        model = Category
        fields = ["uid", "name", "restaurant", "image", "created", "updated"]


class LiteMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["uid", "name", "image", "menu_type", "available", "half_price", "full_price", "description", "ingredients"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = SerializedRelationField("uid", Category.objects, LiteCategorySerializer)

    class Meta:
        model = MenuItem
        fields = ["uid", "name", "image", "category", "menu_type", "available", "half_price", "full_price", "description", "ingredients", "created", "updated"]
