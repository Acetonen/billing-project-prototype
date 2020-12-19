from django.contrib.auth import get_user_model

from project.accounts.data import UserData
from project.core.repos import ORMRepo

UserModel = get_user_model()


class UserRepoFactory:
    @staticmethod
    def get():
        return ORMRepo(database_class=UserModel, data_class=UserData)


UserRepo = UserRepoFactory().get()
