from django.db import models

from project.core.models import TimeStampParentModel


class Transaction(TimeStampParentModel):
    uuid = models.UUIDField(db_index=True)
    sender = models.ForeignKey(
        "payments.Wallet",
        on_delete=models.CASCADE,
        related_name="requested_transactions",
        null=True,
    )
    receiver = models.ForeignKey(
        "payments.Wallet",
        on_delete=models.CASCADE,
        related_name="received_transactions",
    )
    sum = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    done_time = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(
        default=True,
        help_text="only invoices can be is_done=False until they hasn't payment",
    )

    def __str__(self):
        type_ = "transaction" if self.is_done else "invoice"
        return f"{type_} on sum: {self.sum}, number: {self.uuid}"
