from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_bdd import scenario, when

from project.payments.tests.conftest import EXAMPLE_CONVERTERS

UserModel = get_user_model()


@scenario(
    "features/balance.feature",
    "Check balance",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_check_balance():
    pass


@when("I request my balance")
def request_balance(ac, sender_user, response):
    ac.force_authenticate(user=sender_user)
    response["information"] = ac.get(reverse("balance"))
