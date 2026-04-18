from django.contrib.auth.models import User
from django.db import models

from shared.common.abstract_models import CreateUpdate


class Chain(CreateUpdate):
    name = models.CharField(max_length=512)

    def __str__(self):
        return self.name


class UserProfile(CreateUpdate):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    is_guest = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} / {self.user}"

    @property
    def full_name(self):
        return self.user.get_full_name()
