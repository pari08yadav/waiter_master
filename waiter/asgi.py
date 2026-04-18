import os

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "waiter.settings")

from django.core.asgi import get_asgi_application

asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter

from orders.routing import routes

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": routes,
})
