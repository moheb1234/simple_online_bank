import random
from abc import ABC, abstractmethod

from django.db import models

from customer.models import Customer


class BankAccount(models.Model):
    account_number = models.CharField(max_length=16, unique=True, default='')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    created_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    account_balance = models.PositiveIntegerField(default=0)
    account_type = models.CharField(max_length=15, null=False, blank=False)

    def check_amount(self, amount):
        if amount <= 0:
            raise ValueError('invalid amount')

    def deposit(self, amount):
        self.check_amount(amount)
        self.account_balance += amount
        self.save()

    def withdraw(self, amount):
        self.check_amount(amount)
        if self.account_balance < amount:
            raise ValueError('balance is not enough')
        self.account_balance -= amount
        self.save()

    def fund_transfer(self, to_account, amount):
        if isinstance(to_account, BankAccount):
            if to_account.account_number == self.account_number:
                raise ValueError('accounts cant be equals')
            self.withdraw(amount)
            to_account.deposit(amount)

    def generate_account_number(self):
        self.account_number = ''
        for i in range(16):
            d = random.randrange(0, 10)
            self.account_number += str(d)


class BaseTransaction(models.Model):
    amount = models.PositiveIntegerField()
    explains = models.TextField(default='', blank=True)
    tracking_number = models.CharField(max_length=10, unique=True, null=True)

    class Meta:
        abstract = True

    @staticmethod
    def generate_tracking_number():
        num = ''
        for i in range(10):
            d = random.randrange(0, 10)
            num += str(d)
        return num


class DepositTransaction(BaseTransaction):
    account_number = models.CharField(max_length=16)
    deposit_date = models.DateField(auto_now_add=True)
    account_balance = models.PositiveIntegerField(blank=True)


class WithdrawTransaction(BaseTransaction):
    account_number = models.CharField(max_length=16)
    withdraw_date = models.DateField(auto_now_add=True)
    account_balance = models.PositiveIntegerField(blank=True)


class FundTransferTransaction(BaseTransaction):
    from_account_number = models.CharField(max_length=16, blank=False)
    to_account_number = models.CharField(max_length=16, blank=False)
    to_username = models.CharField(max_length=20, blank=True)
    fund_transfer_date = models.DateField(auto_now_add=True)
