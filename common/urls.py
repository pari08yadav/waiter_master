from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from common import views

router = DefaultRouter()

router.register("user", views.UserViewSet, basename="user")
router.register(
    "user-profile", views.UserProfileViewSet, basename="user-profile"
)
router.register("restaurant", views.RestaurantViewSet, basename="restaurant")
router.register("table", views.TableViewSet, basename="table")
router.register("category", views.CategoryViewSet, basename="category")
router.register("menu-item", views.MenuItemViewSet, basename="menu-item")
router.register("order", views.OrderViewSet, basename="order")

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("order/<str:uid>/", views.OrderAPIView.as_view(), name="order"),

    # Dashboard (Django template)
    path("dashboard/", views.DashboardPage.as_view(), name="dashboard"),
    path("dashboard/restaurant/<uuid:uid>/", views.RestaurantDetailPage.as_view(), name="dashboard-restaurant"),
    path("dashboard/category/<uuid:uid>/", views.CategoryDetailPage.as_view(), name="dashboard-category"),
    path("dashboard/order/<uuid:uid>/", views.OrderDashboardPage.as_view(), name="dashboard-order"),

    # Dashboard CRUD
    path("dashboard/restaurant/create/", views.RestaurantCreateView.as_view(), name="restaurant-create"),
    path("dashboard/restaurant/<uuid:uid>/delete/", views.RestaurantDeleteView.as_view(), name="restaurant-delete"),
    path("dashboard/restaurant/<uuid:uid>/table/create/", views.TableCreateView.as_view(), name="table-create"),
    path("dashboard/restaurant/<uuid:uid>/table/delete/", views.TableDeleteView.as_view(), name="table-delete"),
    path("dashboard/restaurant/<uuid:uid>/import/", views.CategoryImportView.as_view(), name="category-import"),
    path("dashboard/category/create/", views.CategoryCreateView.as_view(), name="category-create"),
    path("dashboard/category/<uuid:uid>/delete/", views.CategoryDeleteView.as_view(), name="category-delete"),
    path("dashboard/menu-item/create/", views.MenuItemCreateView.as_view(), name="menu-item-create"),
    path("dashboard/menu-item/<uuid:uid>/delete/", views.MenuItemDeleteView.as_view(), name="menu-item-delete"),

    # Table (customer)
    path("table/<uuid:table_uid>/", views.TableMenuPage.as_view(), name="table"),
    path("table/<uuid:table_uid>/order/", views.TableOrderPage.as_view(), name="table-order"),

    re_path("", views.HomePage.as_view(), name="home"),
]
