from django.core.files.base import ContentFile
from django.db import models

from accounts.models import Chain
from shared.common.abstract_models import CreateUpdate
from shared.common.model_helpers import attach_qr
from shared.common.storage_backends import PublicMediaStorage
from shared.common.taxonomies import MenuType


class Restaurant(CreateUpdate):
    name = models.CharField(max_length=512)
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)

    @property
    def table_count(self):
        return self.table_set.count()

    @property
    def category_count(self):
        return self.category_set.count()

    def __str__(self):
        return f"{self.name} / {self.chain}"


class Table(CreateUpdate):
    number = models.PositiveIntegerField(default=0)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to="")
    qr_code_response = models.JSONField(default=dict, blank=True)

    def qr_code_url(self):
        return self.qr_code_response.get("secure_url", None)

    def __str__(self):
        return f"{self.number} / {self.restaurant}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr_bytes = attach_qr(self.uid).getvalue()
            self.qr_code.save(f"QR_{self.uid}.png", ContentFile(qr_bytes), save=False)
        super().save(*args, **kwargs)


class Category(CreateUpdate):
    name = models.CharField(max_length=512)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, storage=PublicMediaStorage())

    def __str__(self):
        return f"{self.name} / {self.restaurant}"

    class Meta:
        verbose_name_plural = "Categories"


class MenuItem(CreateUpdate):
    name = models.CharField(max_length=512)
    image = models.ImageField(blank=True, null=True, storage=PublicMediaStorage())
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    menu_type = models.CharField(max_length=8, choices=MenuType.choices, default=MenuType.VEG)
    available = models.BooleanField(default=True)
    half_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    full_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} / {self.category}"
