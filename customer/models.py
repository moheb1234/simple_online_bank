import random

from django.contrib.auth.models import User
from django.db import models


class Customer(User):
    is_verified = models.BooleanField(default=False)
    verify_code = models.CharField(max_length=6)
    city = models.CharField(max_length=10, blank=False)
    address = models.TextField(blank=False)

    def generate_verify_code(self):
        self.verify_code = str(random.randrange(100000, 999999))
