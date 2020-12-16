from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import CIEmailField
from django.db import models

from project.accounts.managers import UserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    objects = UserManager()

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = CIEmailField(unique=True)
    is_staff = models.BooleanField(
        db_index=True,
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        db_index=True,
        default=True,
        help_text="Designates whether this user should be treated as active."
        " Unselect this instead of deleting accounts.",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
