from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_bdd import scenario, when, then, given

from project.payments.models import Transaction
from project.payments.tests.conftest import EXAMPLE_CONVERTERS

UserModel = get_user_model()


# Scenarios
# -----------------------------------------------------------------------
@scenario(
    "features/invoices.feature",
    "Create invoice",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_create_invoice():
    pass


@scenario(
    "features/invoices.feature",
    "Pay for invoice succeed",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_pay_for_invoice_succeed():
    pass


@scenario(
    "features/invoices.feature",
    "Not enough money to pay invoice",
    example_converters=EXAMPLE_CONVERTERS,
)
def test_not_enough_money_to_pay_invoice():
    pass


# Given
# -----------------------------------------------------------------------
@given(
    "He create invoice with <transfer> sum for me",
    target_fixture="incoming_invoice_uuid",
)
def incoming_invoice_uuid(ac, transfer, receiver_user, sender_user):
    ac.force_authenticate(user=receiver_user)
    data = {
        "user_email": sender_user.email,
        "sum": transfer,
    }
    response = ac.post(reverse("transaction-create-invoice"), data=data, format="json")

    return response.data["uuid"]


# When
# -----------------------------------------------------------------------
@when("I create invoice for <transfer> to this user")
def create_invoice_for_another_user(ac, sender_user, receiver_user, response, transfer):
    ac.force_authenticate(user=sender_user)
    data = {
        "user_email": receiver_user.email,
        "sum": transfer,
    }
    response["information"] = ac.post(
        reverse("transaction-create-invoice"), data=data, format="json"
    )


@when("I pay invoice to this user")
def pay_incoming_invoice(
        ac, sender_user, receiver_user, incoming_invoice_uuid, response
):
    ac.force_authenticate(user=sender_user)
    response["information"] = ac.post(
        reverse("transaction-pay-invoice"),
        data={"uuid": incoming_invoice_uuid},
        format="json",
    )


# Then
# -----------------------------------------------------------------------
@then("There are invoice information in response with <transfer> sum")
def check_success_invoice(response, transfer):
    assert response["information"].data == {
        "done_time": None,
        "id": 1,
        "is_done": False,
        "sum": str(transfer),
        "uuid": str(Transaction.objects.get(is_done=False).uuid),
    }, "not correct invoice in response"
