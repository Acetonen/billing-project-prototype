from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_bdd import scenario, when

from project.factories import WalletFactory
from project.payments.tests.conftest import EXAMPLE_CONVERTERS

UserModel = get_user_model()


# Scenarios
# -----------------------------------------------------------------------
@scenario(
    "features/make_deposits.feature",
    "Make deposits for self",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_make_deposits_for_self():
    pass


@scenario(
    "features/make_deposits.feature",
    "Make deposits for another user",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_make_deposits_for_another_user():
    pass


# When
# -----------------------------------------------------------------------
@when("I make deposits <transfer> to my wallet")
def make_deposits_to_self(ac, sender_user, response, transfer):
    ac.force_authenticate(user=sender_user)
    data = {
        "user_email": sender_user.email,
        "sum": transfer,
    }
    response["information"] = ac.post(
        reverse("transaction-make-deposits"), data=data, format="json"
    )


@when("I make deposits <transfer> to his wallet")
def make_deposits_to_another(ac, receiver_user, response, transfer):
    ac.force_authenticate(user=WalletFactory().user)

    data = {
        "user_email": receiver_user.email,
        "sum": transfer,
    }
    response["information"] = ac.post(
        reverse("transaction-make-deposits"), data=data, format="json"
    )
