from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .email import send_verifying_code
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from customer.models import Customer
from customer.serializer import CustomerSignupSerializer, CustomerLoginSerializer


@api_view(['POST'])
def signup(request):
    ser_customer = CustomerSignupSerializer(data=request.data)
    if ser_customer.is_valid():
        del ser_customer.validated_data['retype_password']
        customer = ser_customer.save()
        customer.generate_verify_code()
        customer.save()
        if send_verifying_code(customer):
            return Response(ser_customer.data, status=status.HTTP_200_OK)
        customer.delete()
        return Response({'details': 'connections timeout please try agine'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(ser_customer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    ser_data = CustomerLoginSerializer(data=request.data)
    if ser_data.is_valid():
        username = ser_data.validated_data['username']
        password = ser_data.validated_data['password']
        customer = Customer.objects.filter(username=username).first()
        if customer:
            if check_password(password, customer.password):
                if not customer.is_verified:
                    return Response({'details': 'you need to verify your email'})
                access_token = AccessToken.for_user(customer)
                refresh_token = RefreshToken.for_user(customer)
                ser_data.validated_data['access_token'] = str(access_token)
                ser_data.validated_data['refresh_token'] = str(refresh_token)
                del ser_data.validated_data['password']
                return Response(ser_data.validated_data, status=status.HTTP_200_OK)
            return Response({'details': 'password is wrong'})
        return Response({'details': ' user not found'}, status=status.HTTP_403_FORBIDDEN)
    return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def verify_code(request, code):
    customer = Customer.objects.filter(verify_code=code).first()
    if not customer:
        return Response({'details': 'invalid code'}, status=status.HTTP_400_BAD_REQUEST)
    if customer.is_verified:
        return Response({'details': 'your email is verified before'}, status=status.HTTP_400_BAD_REQUEST)
    customer.verify_code = ''
    customer.is_verified = True
    customer.save()
    return Response({'message': 'email verified successfully'})
