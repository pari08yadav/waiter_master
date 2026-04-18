from django.urls import path
from rest_framework.routers import DefaultRouter

from orders.interfaces.http import views as order_views

api_router = DefaultRouter()
api_router.register("order", order_views.OrderViewSet, basename="order")

urlpatterns = [
    path("dashboard/order/<uuid:uid>/", order_views.OrderDashboardPage.as_view(), name="dashboard-order"),
    path("table/<uuid:table_uid>/order/", order_views.TableOrderPage.as_view(), name="table-order"),
    path("order/<str:uid>/", order_views.OrderAPIView.as_view(), name="order"),
]
