"""Compatibility facade for legacy common.tasks imports."""

from restaurants.tasks import import_menu_items

__all__ = ["import_menu_items"]
