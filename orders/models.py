from django.core.exceptions import ValidationError
from django.db import models

from shared.common.abstract_models import CreateUpdate
from shared.common.taxonomies import OrderStatus, PriceType
from restaurants.models import MenuItem, Table


class Order(CreateUpdate):
    session_uid = models.UUIDField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.PENDING, max_length=32)

    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def total_price(self):
        return sum(i.total_price for i in self.orderitem_set.all())

    def __str__(self):
        return f"{self.table} / {self.status}"


class OrderItem(CreateUpdate):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    price_type = models.CharField(choices=PriceType.choices, default=PriceType.FULL, max_length=8)
    quantity = models.PositiveIntegerField()

    @property
    def price(self):
        return self.menu_item.full_price if self.price_type == PriceType.FULL else self.menu_item.half_price

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.order} / {self.menu_item} / {self.quantity}"

    def clean(self):
        if self.order.table.restaurant != self.menu_item.category.restaurant:
            raise ValidationError({"table": "Table not found."})
