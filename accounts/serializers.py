from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import Chain, UserProfile
from shared.common.taxonomies import MenuType, OrderStatus, serialize


class ChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chain
        fields = ["name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.CharField(source="user.email")
    chain_name = serializers.CharField(source="chain.name")
    is_staff = serializers.BooleanField(source="user.is_staff", read_only=True)
    raw_password = serializers.CharField(write_only=True, required=False)
    choices = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["full_name", "username", "email", "uid", "chain_name", "created", "updated", "choices", "is_staff", "raw_password"]

    def get_choices(self, instance):
        return {"menu_type": serialize(MenuType), "order_status": serialize(OrderStatus)}

    def validate(self, attrs):
        if "request" in self.context:
            user_instance = self.context["request"].user
            user = User(**attrs.get("user"))
            if user_instance.username != user.username:
                user.validate_unique()
        return super().validate(attrs)

    def create(self, validated_data):
        user = User(**validated_data.pop("user"))
        user.set_password(raw_password=validated_data.pop("raw_password"))
        instance = UserProfile(**validated_data)
        instance.user = user
        user.save()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if "request" in self.context:
            user_instance = self.context["request"].user
            user = User(**validated_data.pop("user"))
            instance.user.username = user.username
            instance.user.email = user.email
            instance.user.save()
            if "raw_password" in validated_data:
                user_instance.set_password(raw_password=validated_data.pop("raw_password"))
                user_instance.save()
        return super().update(instance, validated_data)


class LiteUserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["username", "email", "uid"]
