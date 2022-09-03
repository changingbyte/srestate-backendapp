import imp

from marshmallow import ValidationError
from UserManagement.models import BrokersUsers ,User
from property.models import Broker
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth.models import BaseUserManager


class UserLoginSerializer(serializers.Serializer):
    Mobile = serializers.CharField(max_length = 10)
    appString = serializers.CharField(max_length = 50)
    def validate_Mobile(self,value):
        if len(value) != 10:
            raise serializers.ValidationError("mobile length error")
        return str(value)


class AuthBrokersUserserializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
         model = User
         fields = ('name','mobile','auth_token','otp','is_premium','is_profile_completed')
    
    def get_auth_token(self, obj):
        token = Token.objects.get_or_create(user=obj)
        print(token)
        print(token[0])
        return token[0].key

    def get_name(self,obj):
        try:
            brokeruser = Broker.objects.get(mobile = obj.mobile)
            return brokeruser.name
        except Broker.DoesNotExist:
            return None
        




class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = BrokersUsers
        fields = ('Mobile',)

    def validate_mobile(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("mobile length error")
        return str(value)

    # def validate_otp(self, value):
    #     user = User.objects.filter(mobile=value)
    #     if user.otp == value:
    #         return value
    #     else:
    #         raise ValidationError("Invalid OTP")