from django.contrib.auth import get_user_model
from django.urls import reverse

from project.payments.models import Wallet

UserModel = get_user_model()


def test_auto_user_and_wallet_creation(ac):
    assert Wallet.objects.count() == 0
    assert UserModel.objects.count() == 0

    data = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "email": "email@email.com",
        "password": "admin12345678",
    }

    response = ac.post(reverse("api-registration"), data=data, format="json")

    assert response.status_code == 200
    assert Wallet.objects.count() == 1
    assert UserModel.objects.count() == 1
