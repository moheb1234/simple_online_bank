from django.contrib import admin

from bank_account.models import BankAccount, DepositTransaction, WithdrawTransaction, FundTransferTransaction

admin.site.register(BankAccount)
admin.site.register(DepositTransaction)
admin.site.register(WithdrawTransaction)
admin.site.register(FundTransferTransaction)
