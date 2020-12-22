from decimal import Decimal

import pytest
from pytest_bdd import then, given

from project.factories import WalletFactory
from project.payments.models import Transaction

EXAMPLE_CONVERTERS = dict(
    sender_start=Decimal,
    receiver_start=Decimal,
    transfer=Decimal,
    sender_result=Decimal,
    receiver_result=Decimal,
    receiver_email=str,
)


# Fixtures
# -----------------------------------------------------------------------
@pytest.fixture
def response():
    return {"information": None}


# Given
# -----------------------------------------------------------------------
@given("I'm user with <sender_start> on my wallet", target_fixture="sender_user")
def sender_user(sender_start):
    wallet = WalletFactory(balance=sender_start)
    return wallet.user


@given(
    "We have user with <receiver_email> with <receiver_start> balance in database",
    target_fixture="receiver_user",
)
def receiver_user(receiver_email, receiver_start):
    receiver = WalletFactory(balance=receiver_start, user__email=receiver_email).user

    return receiver


@then("There is no transactions in database")
@given("There is no transactions in database")
def no_transaction_in_database():
    assert (
        Transaction.objects.count() == 0
    ), "there are already transactions in database"


# Then
# -----------------------------------------------------------------------
@then("Operation succeeded")
def check_operation_succeeded(response):
    assert response["information"] is not None, "no response information"
    assert response["information"].status_code == 200, "response status code is not 200"


@then("Operation isn't succeeded")
def check_operation_succeeded(response):
    assert response["information"] is not None, "no response information"
    assert response["information"].status_code != 200, "response status code is 200"


@then("There are <sender_result> in response with my wallet information")
def check_money_in_response(sender_result, response):
    assert response["information"].data == {
        "currency": "usd",
        "balance": str(sender_result),
    }


@then("There are success response")
def check_success_response(response):
    assert response["information"].data == {
        "details": "success"
    }, "response doesn't success"


@then("There are 'not enough money' error message in response")
def check_success_response(response):
    assert response["information"].data == {
        "code": "invalid",
        "errors": "Not enough money to make transfer.",
        "message": "Not enough money to make transfer.",
        "status": "validation_error",
        "status_code": 400,
    }, "response is success"


@then("There is one transaction record in database")
def check_transactions_in_database():
    assert (
        Transaction.objects.filter(is_done=True).count() == 1
    ), "transaction doesn't created in database"


@then("There is one invoice record in database")
def check_invoice_in_database():
    assert (
        Transaction.objects.filter(is_done=False).count() == 1
    ), "invoice doesn't created in database"


@then("There is no invoice record in database")
def check_invoice_in_database():
    assert (
        Transaction.objects.filter(is_done=False).count() == 0
    ), "invoice doesn't created in database"


@then("My wallet balance is <sender_result>")
def check_my_wallet_balance(sender_user, sender_result):
    sender_user.refresh_from_db()
    assert sender_user.wallet.balance == sender_result


@then("His wallet balance is <receiver_result>")
def check_his_wallet_balance(receiver_user, receiver_result):
    receiver_user.refresh_from_db()
    assert receiver_user.wallet.balance == receiver_result
