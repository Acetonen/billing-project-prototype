from django.urls import path
from rest_framework.routers import DefaultRouter

from project.payments.views import BalanceView, TransactionsViewSet

router = DefaultRouter()

router.register(r"transactions", TransactionsViewSet)

urlpatterns = [
    path("balance/", BalanceView.as_view(), name="balance"),
] + router.urls
