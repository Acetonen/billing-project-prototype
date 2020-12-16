from decimal import Decimal

from factory import SubFactory, Faker
from factory.django import DjangoModelFactory

from project.accounts.models import CustomUser
from project.payments.models import Wallet


class UserFactory(DjangoModelFactory):
    first_name = "BORIS"
    email = Faker("email")
    is_staff = False

    class Meta:
        model = CustomUser
        django_get_or_create = ["email"]


class WalletFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    balance = Decimal("666.00")

    class Meta:
        model = Wallet
