"""Compatibility facade for legacy common.views imports.

Business logic now lives in domain apps:
- accounts.views
- restaurants.views
- orders.views
"""

from django.views.generic import TemplateView

from accounts.views import LoginView, LogoutView, UserProfileViewSet, UserViewSet, is_ajax
from orders.views import (
    OrderAPIView,
    OrderDashboardPage,
    OrderViewSet,
    TableOrderPage,
    is_valid_uid,
)
from restaurants.views import (
    CategoryCreatePageView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryDetailPage,
    CategoryEditView,
    CategoryImportView,
    CategoryViewSet,
    DashboardPage,
    MenuItemCreateView,
    MenuItemDeleteView,
    MenuItemFormView,
    MenuItemViewSet,
    RestaurantCategoriesPage,
    RestaurantCreateView,
    RestaurantDeleteView,
    RestaurantDetailPage,
    RestaurantTablesPage,
    RestaurantViewSet,
    TableCreateView,
    TableDeleteView,
    TableMenuPage,
    TableViewSet,
)
from shared.common.mixins import AuthMixin


class HomePage(TemplateView):
    template_name = "common/home.html"


# Legacy class name preserved for backward compatibility.
Logout = LogoutView

__all__ = [
    "AuthMixin",
    "HomePage",
    "DashboardPage",
    "RestaurantDetailPage",
    "RestaurantTablesPage",
    "RestaurantCategoriesPage",
    "CategoryDetailPage",
    "CategoryEditView",
    "MenuItemFormView",
    "TableMenuPage",
    "TableOrderPage",
    "OrderDashboardPage",
    "RestaurantCreateView",
    "RestaurantDeleteView",
    "TableCreateView",
    "TableDeleteView",
    "CategoryCreatePageView",
    "CategoryCreateView",
    "CategoryDeleteView",
    "CategoryImportView",
    "MenuItemCreateView",
    "MenuItemDeleteView",
    "LoginView",
    "Logout",
    "LogoutView",
    "UserProfileViewSet",
    "UserViewSet",
    "RestaurantViewSet",
    "TableViewSet",
    "CategoryViewSet",
    "MenuItemViewSet",
    "OrderViewSet",
    "OrderAPIView",
    "is_ajax",
    "is_valid_uid",
]
