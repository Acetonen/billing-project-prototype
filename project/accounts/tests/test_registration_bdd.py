from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_bdd import scenario, given, when, then

from project.payments.models import Wallet

UserModel = get_user_model()


@scenario("features/registration.feature", "New user registration")
def test_registration():
    pass


@given("I'm a new user", target_fixture="new_user")
def new_user():
    return {"registration_result": None}


@then("There is no users and wallets in database yet")
def empty_database():
    assert Wallet.objects.count() == 0, "wallet already in database"
    assert UserModel.objects.count() == 0, "user already in database"


@when("I send registrations credentials")
def send_registration_credentials(ac, new_user):
    data = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "email": "email@email.com",
        "password": "admin12345678",
    }

    new_user["registration_result"] = ac.post(
        reverse("api-registration"), data=data, format="json"
    )


@then("I should registered success")
def send_registration_credentials(new_user):
    assert new_user["registration_result"] is not None
    assert (
        new_user["registration_result"].status_code == 200
    ), "registration not success"


@then("There are one user and one wallet in database")
def send_registration_credentials():
    assert Wallet.objects.count() == 1, "no new wallet in database"
    assert UserModel.objects.count() == 1, "no new user in database"
