from django.contrib.auth import get_user_model

from project.payments.models import Wallet

UserModel = get_user_model()


class CreateWalletInteractor:
    """Create user wallet."""

    def set_params(self, user: UserModel) -> "CreateWalletInteractor":
        self.user = user

        return self

    def execute(self) -> Wallet:
        return Wallet.objects.create(user=self.user)
