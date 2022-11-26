from rest_framework import serializers

from bank_account.models import BankAccount, DepositTransaction, FundTransferTransaction, WithdrawTransaction


class BankAccountSerializer(serializers.ModelSerializer):
    customer = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = BankAccount
        fields = ['account_number', 'account_balance', 'account_type', 'customer']


class DepositTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositTransaction
        fields = '__all__'


class WithdrawTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawTransaction
        fields = '__all__'


class FundTransferTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundTransferTransaction
        fields = '__all__'
