import uuid

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from loguru import logger
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from shared.common.mixins import AuthMixin
from shared.common.taxonomies import OrderStatus
from orders.application.services.order_service import OrderService
from orders.models import Order
from orders.serializers import OrderSerializer
from restaurants.models import Table


def is_valid_uid(uid, version=4) -> bool:
    try:
        uuid.UUID(uid, version=version)
    except ValueError:
        return False
    return True


class TableOrderPage(TemplateView):
    template_name = "orders/table/order.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        table = get_object_or_404(Table, uid=kwargs["table_uid"])
        session_uid = self.request.session.get("uid", str(uuid.uuid4()))
        self.request.session["uid"] = session_uid
        orders = Order.objects.filter(table=table, session_uid=session_uid).prefetch_related("orderitem_set__menu_item")
        ctx["table"] = table
        ctx["orders"] = orders
        ctx["total_price"] = sum(o.total_price for o in orders)
        ctx["session_uid"] = session_uid
        return ctx


class OrderDashboardPage(AuthMixin, TemplateView):
    template_name = "orders/dashboard/order.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from restaurants.models import Restaurant
        restaurant = get_object_or_404(Restaurant, uid=kwargs["uid"], chain=self.request.chain)
        status_filter = self.request.GET.get("status", "")
        orders = Order.objects.filter(table__restaurant=restaurant).prefetch_related("orderitem_set__menu_item").order_by("-created")
        if status_filter:
            orders = orders.filter(status=status_filter)
        ctx["restaurant"] = restaurant
        ctx["orders"] = orders
        ctx["status_filter"] = status_filter
        ctx["order_statuses"] = OrderStatus.choices
        ctx["user_profile"] = self.request.profile
        return ctx


class OrderAPIView(APIView):
    def get(self, request, *args, **kwargs):
        uid = kwargs.get("uid")
        if not uid or not is_valid_uid(uid):
            raise Http404
        summary = OrderService.get_order_summary(uid, request)
        return Response(
            {
                "table": summary.table,
                "orders": summary.orders,
                "session_uid": summary.session_uid,
                "total_price": summary.total_price,
            },
            status=HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        uid = kwargs.get("uid")
        if not uid or not is_valid_uid(uid):
            raise Http404
        try:
            order = OrderService.place_order_from_cookie(uid, request)
        except ValueError as exc:
            return JsonResponse({"detail": str(exc)}, status=400)
        OrderService.broadcast_order_update(order)
        return Response({"status": "success"}, status=HTTP_200_OK)


class OrderViewSet(AuthMixin, ModelViewSet):
    lookup_field = "uid"
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ("table__restaurant__uid", "status")
    ordering_fields = ("created",)
    http_method_names = ("get",)

    def get_queryset(self):
        return Order.objects.filter(table__restaurant__chain=self.request.chain)
