from django.urls import path
from rest_framework.routers import DefaultRouter

from project.payments.views_wrappers import (
    BalanceViewWrapper,
    TransactionsViewSetWrapper,
)

router = DefaultRouter()

router.register(r"transactions", TransactionsViewSetWrapper)

urlpatterns = [
    path("balance/", BalanceViewWrapper.as_view(), name="balance"),
] + router.urls
