from operator import mod
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

### not in use
class BrokersUsers(models.Model):
    user_id = models.CharField(max_length=30, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be entered in the format: '999999999'. 10 digit mobile number.")
    Mobile = models.CharField(validators=[phone_regex], max_length=10, blank=True , unique= True) # validators should be a list
    name = models.CharField(max_length=30, blank=True, null=True)
    otp = models.CharField(max_length=30, blank=True, null=True)

#     def __str__(self):
#         return str(self.Mobile)+str(self.id)


class User(AbstractUser):
    mobile = models.CharField(max_length=10)
    balance = models.IntegerField(default=0)
    otp = models.CharField(max_length=30, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    is_profile_completed = models.BooleanField(default=False)