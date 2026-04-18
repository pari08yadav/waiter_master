import json

from django.shortcuts import get_object_or_404
from django.urls import reverse

from restaurants.models import Category, Restaurant, Table


class DashboardService:
    """Application service for dashboard page context assembly."""

    @staticmethod
    def get_chain_dashboard_context(request) -> dict:
        from orders.models import Order

        restaurants = Restaurant.objects.filter(chain=request.chain).order_by("name")
        for restaurant in restaurants:
            restaurant.order_count = Order.objects.filter(
                table__restaurant=restaurant
            ).count()

        return {
            "restaurants": restaurants,
            "user_profile": request.profile,
            "NOTIFY_WS_DATA": json.dumps(
                [
                    {
                        "rid": str(restaurant.uid),
                        "url": reverse(
                            "common:dashboard-order",
                            kwargs={"uid": str(restaurant.uid)},
                        ),
                    }
                    for restaurant in restaurants
                ]
            ),
        }

    @staticmethod
    def get_restaurant_overview_context(request, restaurant_uid) -> dict:
        restaurant = get_object_or_404(
            Restaurant, uid=restaurant_uid, chain=request.chain
        )
        return {
            "restaurant": restaurant,
            "tables_count": Table.objects.filter(restaurant=restaurant).count(),
            "categories_count": Category.objects.filter(restaurant=restaurant).count(),
            "user_profile": request.profile,
            "NOTIFY_WS_DATA": json.dumps(
                [
                    {
                        "rid": str(restaurant.uid),
                        "url": reverse(
                            "common:dashboard-order",
                            kwargs={"uid": str(restaurant.uid)},
                        ),
                    }
                ]
            ),
        }
