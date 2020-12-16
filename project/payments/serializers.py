from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from project.core.serializers import ParentSerializer
from project.payments.models import Transaction

UserModel = get_user_model()


class WalletSerializer(ParentSerializer):
    currency = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True)


class TransactionCreateSerializer(ParentSerializer):
    sum = serializers.DecimalField(max_digits=9, decimal_places=2, required=True)
    user_email = serializers.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", False)
        self.is_transfer = kwargs.pop(
            "is_transfer", False
        )  # to check transfer validation.
        super().__init__(*args, **kwargs)

    def validate_user_email(self, data):
        try:
            UserModel.objects.get(email=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Receiver email does not exists.")

        return data

    def validate_sum(self, data):
        if data < 0:
            raise serializers.ValidationError("Sum can't be a negative number.")

        return data

    def validate(self, attrs):
        if self.is_transfer and attrs["user_email"] == self.request.user.email:
            raise serializers.ValidationError("You can't transfer objects to yourself.")

        return attrs


class TransactionSerializer(ParentSerializer):
    id = serializers.IntegerField(read_only=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(read_only=True)
    sum = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True)
    done_time = serializers.DateTimeField(read_only=True, allow_null=True)
    is_done = serializers.BooleanField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)


class InvoicePaySerializer(ParentSerializer):
    uuid = serializers.UUIDField(required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", False)
        super().__init__(*args, **kwargs)

    def validate_uuid(self, data):
        try:
            transaction = Transaction.objects.get(
                uuid=data, sender__user=self.request.user
            )
            print("transaction", transaction)
        except ObjectDoesNotExist:
            print("ObjectDoesNotExist", ObjectDoesNotExist)
            raise serializers.ValidationError("You don't have invoice with such id.")

        if transaction.is_done:
            print("transaction.is_done", transaction.is_done)
            raise serializers.ValidationError("Invoice already paid.")

        print("data", data)
        return data
