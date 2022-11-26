from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bank_account.models import BankAccount, BaseTransaction, DepositTransaction, \
    WithdrawTransaction
from bank_account.serializer import BankAccountSerializer, DepositTransactionSerializer, \
    FundTransferTransactionSerializer, WithdrawTransactionSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account(request):
    account_type = request.query_params['account_type']
    customer = request.user
    account = BankAccount(account_type=account_type, customer_id=customer.id)
    account.generate_account_number()
    account.save()
    ser_account = BankAccountSerializer(instance=account)
    return Response(ser_account.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    ser_data = DepositTransactionSerializer(data=request.data)
    if ser_data.is_valid():
        amount = ser_data.validated_data['amount']
        account_number = ser_data.validated_data['account_number']
        account = BankAccount.objects.filter(account_number=account_number).first()
        if account:
            if account.customer_id == request.user.id:
                try:
                    account.deposit(amount)
                except ValueError as ve:
                    return Response({'details': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
                ser_data.validated_data['account_balance'] = account.account_balance
                ser_data.validated_data['tracking_number'] = BaseTransaction.generate_tracking_number()
                obj = ser_data.save()
                ser_data.validated_data['deposit_date'] = obj.deposit_date
                return Response(ser_data.validated_data, status=status.HTTP_200_OK)
            return Response({'details': 'you dont have permission'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'details': 'account not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    ser_data = WithdrawTransactionSerializer(data=request.data)
    if ser_data.is_valid():
        amount = ser_data.validated_data['amount']
        account_number = ser_data.validated_data['account_number']
        account = BankAccount.objects.filter(account_number=account_number).first()
        if account:
            if account.customer_id == request.user.id:
                try:
                    account.withdraw(amount)
                except ValueError as ve:
                    return Response({'details': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
                ser_data.validated_data['account_balance'] = account.account_balance
                ser_data.validated_data['tracking_number'] = BaseTransaction.generate_tracking_number()
                obj = ser_data.save()
                ser_data.validated_data['withdraw_date'] = obj.withdraw_date
                return Response(ser_data.validated_data, status=status.HTTP_200_OK)
            return Response({'details': 'you dont have permission'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'details': 'account not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fund_transfer(request):
    ser_data = FundTransferTransactionSerializer(data=request.data)
    if ser_data.is_valid():
        from_account = BankAccount.objects.filter(account_number=ser_data.validated_data['from_account_number']).first()
        to_account = BankAccount.objects.filter(account_number=ser_data.validated_data['to_account_number']).first()
        amount = ser_data.validated_data['amount']
        if to_account and from_account:
            if from_account.customer.id == request.user.id:
                try:
                    from_account.fund_transfer(to_account, amount)
                except ValueError as ve:
                    return Response({'details': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
                ser_data.validated_data['to_username'] = to_account.customer.username
                ser_data.validated_data['tracking_number'] = BaseTransaction.generate_tracking_number()
                obj = ser_data.save()
                ser_data.validated_data['fund_transfer_date'] = obj.fund_transfer_date
                return Response(ser_data.validated_data, status=status.HTTP_200_OK)
            return Response({'details': 'you dont have permission'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'details': 'account not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transaction(request, tracking_number):
    filtered_deposit_transaction = DepositTransaction.objects.filter(tracking_number=tracking_number)
    filtered_withdraw_transaction = DepositTransaction.objects.filter(tracking_number=tracking_number)
    filtered_fund_transfer_transaction = DepositTransaction.objects.filter(tracking_number=tracking_number)
    if filtered_deposit_transaction.exists() or filtered_withdraw_transaction.exists():
        transaction = filtered_deposit_transaction.first()
        account = BankAccount.objects.filter(account_number=transaction.account_number).first()
        if account.customer_id == request.user.id:
            if isinstance(transaction, WithdrawTransaction):
                ser_transaction = WithdrawTransactionSerializer(instance=transaction)
            else:
                ser_transaction = DepositTransactionSerializer(instance=transaction)
            return Response(ser_transaction.data, status=status.HTTP_200_OK)
        return Response({'details': 'you dont have permission'}, status=status.HTTP_401_UNAUTHORIZED)
    elif filtered_fund_transfer_transaction.exists():
        transaction = filtered_fund_transfer_transaction.first()
        from_account = BankAccount.objects.filter(account_number=transaction.from_account_number).first()
        to_account = BankAccount.objects.filter(account_number=transaction.to_account_number).first()
        if from_account.customer.id == request.user.id or to_account.customer.id == request.user.id:
            ser_transaction = FundTransferTransactionSerializer(instance=transaction)
            return Response(ser_transaction.data, status=status.HTTP_200_OK)
        return Response({'details': 'you dont have permission'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'details': 'transaction not fond'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request, account_number):
    account = BankAccount.objects.filter(account_number=account_number).first()
    if account:
        if account.customer_id == request.user.id:
            account.delete()
            return Response({'message': 'account deleted'}, status=status.HTTP_200_OK)
        return Response({'details': 'you dont have permission'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'details': 'account not found'})
