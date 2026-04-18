from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from accounts.urls import api_router as accounts_api_router
from orders.urls import api_router as orders_api_router
from restaurants.urls import api_router as restaurants_api_router

urlpatterns = [
    path("wtr-adm/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r"api/v1/", include(accounts_api_router.urls)),
    re_path(r"api/v1/", include(restaurants_api_router.urls)),
    re_path(r"api/v1/", include(orders_api_router.urls)),
    re_path(r"^", include(("common.urls", "common"), namespace="common")),
]
