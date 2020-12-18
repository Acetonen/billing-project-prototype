from project.payments.models import Wallet


class CreateWalletInteractor:
    """Create user wallet."""

    def set_params(self, user) -> "CreateWalletInteractor":
        self.user = user

        return self

    def execute(self) -> Wallet:
        return Wallet.objects.create(user=self.user)
