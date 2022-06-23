
from rest_framework import serializers


class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency


class MoneyField(serializers.Field):
    def to_representation(self, value):
        return {
            "amount": value.amount,
            "currency": value.currency
        }

    def to_internal_value(self, data):
        amount = data.get("amount")
        currency = data.get("currency")
        return Money(amount, currency)
