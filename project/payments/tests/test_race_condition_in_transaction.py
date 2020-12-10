import asyncio
import json
from decimal import Decimal

import aiohttp
import requests
from django.urls import reverse

from project.factories import WalletFactory
from project.payments.models import Transaction, Wallet

RECEIVER_EMAIL = 'test_race_condition@test.com'
SENDER_EMAIL = 'login@test.com'


def _register_sender(live_server):
    sender_data = {
        'email': SENDER_EMAIL,
        'password': 'password12345678',
        'first_name': 'Sender',
        'last_name': 'Senderovich'
    }
    register = requests.post(f"{live_server.url}{reverse('api-registration')}",
                             data=sender_data)
    assert register.status_code == 200, register.text
    login = requests.post(f"{live_server.url}{reverse('api-login')}",
                          data=sender_data)
    assert login.status_code == 200, login.text

    return f"JWT {login.json()['token']}"


def test_transfer_to_another_user_with_lag_success(live_server, event_loop, settings):
    # Setup
    # -------------------------------------------------------------
    settings.MAKE_TEST_LAG_IN_TRANSFER = True  # set test 2sec lag
    event_loop.set_debug(True)
    URL = f"{live_server.url}{reverse('transaction-transfer-to-another-user')}"
    receiver_wallet = WalletFactory(balance=0,
                                    user__email=RECEIVER_EMAIL)
    sender_token = _register_sender(live_server)
    sender_wallet = Wallet.objects.get(user__email=SENDER_EMAIL)
    sender_wallet.balance = 100
    sender_wallet.save()

    # Test
    # -------------------------------------------------------------
    async def create_transaction_success(client):
        """Initiate firs transaction with 2 sec net lag emulation. It should be success anyway."""
        data = {
            'user_email': RECEIVER_EMAIL,
            'sum': '70',
        }
        async with client.post(URL, data=data) as response:
            text = await response.text()
            assert response.status == 200, text
            assert json.loads(text) == {'balance': '30.00', 'currency': 'usd'}

    async def create_transaction_fail(client):
        """Initiate second transaction simultaneously with first (during first net lag).
        It shouldn't be success if we handle race condition case right away."""
        data = {
            'user_email': RECEIVER_EMAIL,
            'sum': '60',
        }
        await asyncio.sleep(1)  # prevent this transaction to start first
        async with client.post(URL, data=data) as response:
            text = await response.text()
            assert response.status == 400, text
            assert json.loads(text) == {'code': 'invalid',
                                        'errors': 'Not enough money to make transfer.',
                                        'message': 'Not enough money to make transfer.',
                                        'status': 'validation_error',
                                        'status_code': 400}

    async def create_transactions():
        async with aiohttp.ClientSession(headers={'Accept': 'application/json; version=1.0',
                                                  'Authorization': sender_token}) as client:
            await asyncio.gather(
                create_transaction_success(client),
                create_transaction_fail(client)
            )

    event_loop.run_until_complete(
        create_transactions()
    )

    # Final checks
    # -------------------------------------------------------------
    receiver_wallet.refresh_from_db()
    sender_wallet.refresh_from_db()

    assert sender_wallet.balance == Decimal(30)
    assert receiver_wallet.balance == Decimal(70)
    assert Transaction.objects.count() == 1
