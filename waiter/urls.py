# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.urls import include, path, re_path

from common.urls import router

# urlpatterns = [
#     path("wtr-adm/", admin.site.urls),
#     re_path(r"api/v1/", include(router.urls)),
#     re_path(
#         r"^",
#         include(
#             ("common.urls", "common"),
#             namespace="common",
#         ),
#     ),
# ]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path("wtr-adm/", admin.site.urls),
    # 1. Add static/media helper BEFORE the catch-all
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 2. These regex paths should be LAST because they are greedy
urlpatterns += [
    re_path(r"api/v1/", include(router.urls)),
    re_path(
        r"^",
        include(
            ("common.urls", "common"),
            namespace="common",
        ),
    ),
]