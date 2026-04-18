from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

from orders.consumers import OrderConsumer, QueryAuthMiddleware

urlpatterns = [
    path("ws/order/<str:uid>/", OrderConsumer.as_asgi()),
]

routes = AllowedHostsOriginValidator(
    AuthMiddlewareStack(QueryAuthMiddleware(URLRouter(urlpatterns)))
)
