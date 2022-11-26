import re

from django.contrib.auth.hashers import make_password, check_password
from rest_framework import serializers

from customer.models import Customer


class CustomerSignupSerializer(serializers.ModelSerializer):
    retype_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'username', 'password', 'city', 'address', 'email', 'retype_password']

    def validate(self, attrs):
        if not check_password(attrs['retype_password'], attrs['password']):
            raise serializers.ValidationError('password dont match with retype password')
        return attrs

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('password must be at least 8 characters')
        is_valid = re.search('[A-Z]', value)
        if not is_valid:
            raise serializers.ValidationError('password must be contains at least one uppercase')
        is_valid = re.search('[a-z]', value)
        if not is_valid:
            raise serializers.ValidationError('password must be contains at least one lowercase')
        is_valid = re.search('\\d', value)
        if not is_valid:
            raise serializers.ValidationError('password must be contains at least one digit')
        is_valid = re.search('\\W', value)
        if not is_valid:
            raise serializers.ValidationError('password must be contains at least one special character')
        not_valid = re.search('\\s', value)
        if not_valid:
            raise serializers.ValidationError('password must not be contains space')
        return make_password(value)


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, required=True, write_only=True)
    password = serializers.CharField(max_length=20, required=True, write_only=True)
    access_token = serializers.CharField(max_length=100, read_only=True)
    refresh_token = serializers.CharField(max_length=100, read_only=True)
