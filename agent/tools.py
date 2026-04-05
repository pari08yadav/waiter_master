from common.models import Order, Category
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from common.taxonomies import OrderStatus


def get_order_status(session_uid):
    orders = Order.objects.filter(session_uid=session_uid).order_by("-created")[:3]
    return [
        {
            "uid": str(o.uid),
            "status": o.status_display,
            "total_price": str(o.total_price),
            "items": [
                {
                    "name": item.menu_item.name,
                    "quantity": item.quantity,
                    "price": str(item.total_price),
                }
                for item in o.orderitem_set.all()
            ],
        }
        for o in orders
    ]


def get_full_menu(restaurant_id=None):
    qs = Category.objects.prefetch_related("menuitem_set")
    if restaurant_id:
        qs = qs.filter(restaurant_id=restaurant_id)
    menu = []
    for cat in qs:
        items = [
            {
                "name": i.name,
                "type": i.menu_type,
                "full_price": str(i.full_price),
                "half_price": str(i.half_price) if i.half_price else None,
                "description": i.description,
                "available": i.available,
            }
            for i in cat.menuitem_set.all()
        ]
        if items:
            menu.append({"category": cat.name, "items": items})
    return menu


def get_all_orders(restaurant_id):
    orders = Order.objects.filter(
        table__restaurant_id=restaurant_id
    ).prefetch_related("orderitem_set__menu_item").order_by("-created")[:20]
    return [
        {
            "uid": str(o.uid),
            "table": o.table.number,
            "status": o.status_display,
            "total_price": str(o.total_price),
            "created": str(o.created),
            "items": [
                {
                    "name": item.menu_item.name,
                    "quantity": item.quantity,
                    "price": str(item.total_price),
                }
                for item in o.orderitem_set.all()
            ],
        }
        for o in orders
    ]


def update_order_status(order_uid, status):

    valid = [s.value for s in OrderStatus]
    if status.upper() not in valid:
        return {"error": f"Invalid status. Must be one of {valid}"}

    order = Order.objects.filter(uid=order_uid).first()
    if not order:
        return {"error": "Order not found"}

    order.status = status.upper()
    order.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(order.session_uid),
        {"type": "send_order", "order": order},
    )
    async_to_sync(channel_layer.group_send)(
        str(order.table.restaurant.uid),
        {"type": "send_order", "order": order},
    )
    return {"success": True, "order_uid": order_uid, "new_status": status.upper()}
