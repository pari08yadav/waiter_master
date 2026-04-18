"""Compatibility facade for legacy common.forms imports."""

from accounts.forms import LoginForm
from restaurants.forms import CategoryForm, MenuItemForm, RestaurantForm

__all__ = ["LoginForm", "RestaurantForm", "CategoryForm", "MenuItemForm"]
