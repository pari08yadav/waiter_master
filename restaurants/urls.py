from django.urls import path
from rest_framework.routers import DefaultRouter

from restaurants.interfaces.http import views as restaurant_views

api_router = DefaultRouter()
api_router.register("restaurant", restaurant_views.RestaurantViewSet, basename="restaurant")
api_router.register("table", restaurant_views.TableViewSet, basename="table")
api_router.register("category", restaurant_views.CategoryViewSet, basename="category")
api_router.register("menu-item", restaurant_views.MenuItemViewSet, basename="menu-item")

urlpatterns = [
    # Dashboard pages
    path("dashboard/", restaurant_views.DashboardPage.as_view(), name="dashboard"),
    path(
        "dashboard/restaurant/<uuid:uid>/",
        restaurant_views.RestaurantDetailPage.as_view(),
        name="dashboard-restaurant",
    ),
    path(
        "dashboard/restaurant/<uuid:uid>/tables/",
        restaurant_views.RestaurantTablesPage.as_view(),
        name="restaurant-tables",
    ),
    path(
        "dashboard/restaurant/<uuid:uid>/categories/",
        restaurant_views.RestaurantCategoriesPage.as_view(),
        name="restaurant-categories",
    ),
    path(
        "dashboard/category/<uuid:uid>/",
        restaurant_views.CategoryDetailPage.as_view(),
        name="dashboard-category",
    ),
    path(
        "dashboard/category/<uuid:uid>/edit/",
        restaurant_views.CategoryEditView.as_view(),
        name="category-edit",
    ),
    path(
        "dashboard/category/<uuid:uid>/item/",
        restaurant_views.MenuItemFormView.as_view(),
        name="menu-item-form",
    ),
    # Dashboard CRUD
    path(
        "dashboard/restaurant/create/",
        restaurant_views.RestaurantCreateView.as_view(),
        name="restaurant-create",
    ),
    path(
        "dashboard/restaurant/<uuid:uid>/delete/",
        restaurant_views.RestaurantDeleteView.as_view(),
        name="restaurant-delete",
    ),
    path(
        "dashboard/restaurant/<uuid:uid>/table/create/",
        restaurant_views.TableCreateView.as_view(),
        name="table-create",
    ),
    path(
        "dashboard/restaurant/<uuid:uid>/table/delete/",
        restaurant_views.TableDeleteView.as_view(),
        name="table-delete",
    ),
    path(
        "dashboard/restaurant/<uuid:uid>/import/",
        restaurant_views.CategoryImportView.as_view(),
        name="category-import",
    ),
    path(
        "dashboard/restaurant/<uuid:uid>/category/add/",
        restaurant_views.CategoryCreatePageView.as_view(),
        name="category-create-page",
    ),
    path(
        "dashboard/category/create/",
        restaurant_views.CategoryCreateView.as_view(),
        name="category-create",
    ),
    path(
        "dashboard/category/<uuid:uid>/delete/",
        restaurant_views.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
    path(
        "dashboard/menu-item/create/",
        restaurant_views.MenuItemCreateView.as_view(),
        name="menu-item-create",
    ),
    path(
        "dashboard/menu-item/<uuid:uid>/delete/",
        restaurant_views.MenuItemDeleteView.as_view(),
        name="menu-item-delete",
    ),
    # Customer table page
    path("table/<uuid:table_uid>/", restaurant_views.TableMenuPage.as_view(), name="table"),
]
