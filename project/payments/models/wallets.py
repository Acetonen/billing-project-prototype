from django.contrib.auth import get_user_model
from django.db import models
from model_utils import Choices

from project.core.models import TimeStampParentModel


class Wallet(TimeStampParentModel):
    CURRENCIES = Choices(("usd", "USD"))
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    currency = models.CharField(
        choices=CURRENCIES, default=CURRENCIES.usd, max_length=225
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0), name="balance_gte_0"
            ),
        ]

    def __str__(self):
        return str(self.balance)
