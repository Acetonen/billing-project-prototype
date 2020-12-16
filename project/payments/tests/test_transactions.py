from decimal import Decimal

from django.urls import reverse

from project.factories import WalletFactory
from project.payments.models import Transaction

RECEIVER_EMAIL = "test_invoice_create@test.com"
SENDER_EMAIL = "login@test.com"


def test_balance_check(ac):
    # Setup
    # -------------------------------------------------------------
    wallet = WalletFactory(balance=Decimal("777.00"))
    ac.force_authenticate(user=wallet.user)

    # Test
    # -------------------------------------------------------------
    response = ac.get(reverse("balance"))

    # Final checks
    # -------------------------------------------------------------
    assert response.status_code == 200
    assert response.data == {"balance": "777.00", "currency": "usd"}


def test_make_deposits_for_self(ac):
    # Setup
    # -------------------------------------------------------------
    assert Transaction.objects.count() == 0

    wallet = WalletFactory(balance=Decimal(0))
    ac.force_authenticate(user=wallet.user)

    # Test
    # -------------------------------------------------------------
    data = {
        "user_email": wallet.user.email,
        "sum": "666",
    }
    response = ac.post(reverse("transaction-make-deposits"), data=data, format="json")

    # Final checks
    # -------------------------------------------------------------
    wallet.refresh_from_db()
    assert response.status_code == 200
    assert wallet.balance == Decimal(666)
    assert Transaction.objects.count() == 1
    assert response.data == {"balance": "666.00", "currency": "usd"}


def test_make_deposits_for_another(ac):
    # Setup
    # -------------------------------------------------------------
    assert Transaction.objects.count() == 0

    sender = WalletFactory()
    receiver = WalletFactory(balance=0, user__email=RECEIVER_EMAIL)
    ac.force_authenticate(user=sender.user)

    # Test
    # -------------------------------------------------------------
    data = {
        "user_email": RECEIVER_EMAIL,
        "sum": "666",
    }
    response = ac.post(reverse("transaction-make-deposits"), data=data, format="json")

    # Final checks
    # -------------------------------------------------------------
    receiver.refresh_from_db()
    assert response.status_code == 200
    assert receiver.balance == Decimal(666)
    assert Transaction.objects.count() == 1
    assert response.data == {"details": "success"}


def test_transfer_to_another_user_success(ac):
    # Setup
    # -------------------------------------------------------------
    assert Transaction.objects.count() == 0

    sender = WalletFactory(balance=100)
    receiver = WalletFactory(balance=0, user__email=RECEIVER_EMAIL)
    ac.force_authenticate(user=sender.user)

    # Test
    # -------------------------------------------------------------
    data = {
        "user_email": RECEIVER_EMAIL,
        "sum": "70",
    }
    response = ac.post(
        reverse("transaction-transfer-to-another-user"), data=data, format="json"
    )

    # Final checks
    # -------------------------------------------------------------
    receiver.refresh_from_db()
    sender.refresh_from_db()
    assert response.status_code == 200
    assert receiver.balance == Decimal(70)
    assert sender.balance == Decimal(30)
    assert Transaction.objects.count() == 1
    assert response.data == {"balance": "30.00", "currency": "usd"}


def test_transfer_to_another_user_not_success(ac):
    # Setup
    # -------------------------------------------------------------
    assert Transaction.objects.count() == 0

    sender = WalletFactory(balance=100)
    receiver = WalletFactory(balance=0, user__email=RECEIVER_EMAIL)
    ac.force_authenticate(user=sender.user)

    # Test
    # -------------------------------------------------------------
    data = {
        "user_email": RECEIVER_EMAIL,
        "sum": "150",
    }
    response = ac.post(
        reverse("transaction-transfer-to-another-user"), data=data, format="json"
    )

    # Final checks
    # -------------------------------------------------------------
    receiver.refresh_from_db()
    sender.refresh_from_db()
    assert response.status_code == 400
    assert receiver.balance == Decimal(0)
    assert sender.balance == Decimal(100)
    assert Transaction.objects.count() == 0
    assert response.data == {
        "code": "invalid",
        "errors": "Not enough money to make transfer.",
        "message": "Not enough money to make transfer.",
        "status": "validation_error",
        "status_code": 400,
    }


def test_try_transfer_to_self(ac):
    # Setup
    # -------------------------------------------------------------
    assert Transaction.objects.count() == 0

    sender = WalletFactory(balance=100, user__email=RECEIVER_EMAIL)
    ac.force_authenticate(user=sender.user)

    # Test
    # -------------------------------------------------------------
    data = {
        "user_email": RECEIVER_EMAIL,
        "sum": "100",
    }
    response = ac.post(
        reverse("transaction-transfer-to-another-user"), data=data, format="json"
    )

    # Final checks
    # -------------------------------------------------------------
    sender.refresh_from_db()
    assert response.status_code == 400
    assert sender.balance == Decimal(100)
    assert Transaction.objects.count() == 0
    assert response.data == {
        "code": "invalid",
        "errors": [{"detail": "You can't transfer objects to yourself."}],
        "message": "You can't transfer objects to yourself.",
        "status": "validation_error",
        "status_code": 400,
    }


def test_invoice_create(ac):
    # Setup
    # -------------------------------------------------------------
    sender = WalletFactory(user__email=SENDER_EMAIL)
    receiver = WalletFactory(user__email=RECEIVER_EMAIL)
    ac.force_authenticate(user=receiver.user)

    # Test
    # -------------------------------------------------------------
    data = {
        "user_email": SENDER_EMAIL,
        "sum": "666",
    }
    response = ac.post(reverse("transaction-create-invoice"), data=data, format="json")

    # Final checks
    # -------------------------------------------------------------
    assert response.status_code == 200
    assert Transaction.objects.filter(
        receiver__user__email=RECEIVER_EMAIL, is_done=False
    ).exists()


# noinspection DuplicatedCode
def test_invoice_pay_success(ac):
    # Setup
    # -------------------------------------------------------------
    sender = WalletFactory(user__email=SENDER_EMAIL, balance=170)
    receiver = WalletFactory(user__email=RECEIVER_EMAIL, balance=0)
    ac.force_authenticate(user=receiver.user)
    data = {
        "user_email": SENDER_EMAIL,
        "sum": "150",
    }
    response = ac.post(reverse("transaction-create-invoice"), data=data, format="json")
    invoice_uuid = response.data["uuid"]
    # Test
    # -------------------------------------------------------------
    ac.force_authenticate(user=sender.user)
    response = ac.post(
        reverse("transaction-pay-invoice"), data={"uuid": invoice_uuid}, format="json"
    )

    # Final checks
    # -------------------------------------------------------------
    receiver.refresh_from_db()
    sender.refresh_from_db()
    assert response.status_code == 200
    assert sender.balance == 20
    assert receiver.balance == 150
    assert Transaction.objects.filter(uuid=invoice_uuid, is_done=True).exists()
    assert response.data == {"balance": "20.00", "currency": "usd"}


# noinspection DuplicatedCode
def test_invoice_pay_not_enough_money(ac):
    # Setup
    # -------------------------------------------------------------
    sender = WalletFactory(user__email=SENDER_EMAIL, balance=140)
    receiver = WalletFactory(user__email=RECEIVER_EMAIL, balance=0)
    ac.force_authenticate(user=receiver.user)
    data = {
        "user_email": SENDER_EMAIL,
        "sum": "150",
    }
    response = ac.post(reverse("transaction-create-invoice"), data=data, format="json")
    invoice_uuid = response.data["uuid"]
    # Test
    # -------------------------------------------------------------
    ac.force_authenticate(user=sender.user)
    response = ac.post(
        reverse("transaction-pay-invoice"), data={"uuid": invoice_uuid}, format="json"
    )

    # Final checks
    # -------------------------------------------------------------
    receiver.refresh_from_db()
    sender.refresh_from_db()
    assert response.status_code == 400
    assert sender.balance == 140
    assert receiver.balance == 0
    assert Transaction.objects.filter(uuid=invoice_uuid, is_done=False).exists()
    assert response.data == {
        "code": "invalid",
        "errors": "Not enough money to make transfer.",
        "message": "Not enough money to make transfer.",
        "status": "validation_error",
        "status_code": 400,
    }
