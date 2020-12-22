from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_bdd import scenario, when, then

from project.payments.tests.conftest import EXAMPLE_CONVERTERS

UserModel = get_user_model()


# Scenarios
# -----------------------------------------------------------------------
@scenario(
    "features/make_transfer.feature",
    "Transfer to another user success",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_make_transfer_to_another_user_success():
    pass


@scenario(
    "features/make_transfer.feature",
    "Not enough money to make transfer",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_not_enough_money_for_transfer():
    pass


@scenario(
    "features/make_transfer.feature",
    "Can't transfer to yourself",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_can_not_transfer_to_yourself():
    pass


# When
# -----------------------------------------------------------------------
@when("I send <transfer> to his wallet")
def send_money_to_another_user(ac, sender_user, receiver_user, response, transfer):
    ac.force_authenticate(user=sender_user)
    data = {
        "user_email": receiver_user.email,
        "sum": transfer,
    }
    response["information"] = ac.post(
        reverse("transaction-transfer-to-another-user"), data=data, format="json"
    )


@when("I send <transfer> to myself")
def send_money_to_another_user(ac, sender_user, response, transfer):
    ac.force_authenticate(user=sender_user)
    data = {
        "user_email": sender_user.email,
        "sum": transfer,
    }
    response["information"] = ac.post(
        reverse("transaction-transfer-to-another-user"), data=data, format="json"
    )


@then("There are 'can't receive to yourself' error message in response")
def check_success_response(response):
    assert response["information"].data == {
        "code": "invalid",
        "errors": [{"detail": "You can't transfer objects to yourself."}],
        "message": "You can't transfer objects to yourself.",
        "status": "validation_error",
        "status_code": 400,
    }, "response is success"
