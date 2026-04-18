import threading

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from orders.models import Order
from restaurants.models import MenuItem, Table


@receiver(post_save, sender=Table)
def table_save(sender, instance: Table, **kwargs):
    if kwargs["created"]:
        instance.number = instance.restaurant.table_count
        instance.save()


def clear_chat_history():
    for session in Session.objects.all():
        if "chat_history" in session.get_decoded():
            store = SessionStore(session_key=session.session_key)
            store["chat_history"] = []
            store.save()


@receiver(post_save, sender=MenuItem)
@receiver(post_delete, sender=MenuItem)
def menuitem_changed(sender, instance, **kwargs):
    clear_chat_history()
    def index():
        try:
            from agent.vector_store import upsert_menu_item
            upsert_menu_item(item=instance)
        except Exception:
            pass
    threading.Thread(target=index, daemon=True).start()
