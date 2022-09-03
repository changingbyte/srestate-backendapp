from django.contrib.auth import get_user_model, logout
from UserManagement.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view ,authentication_classes, permission_classes
from property.location.location_views import db
from rest_framework.renderers import JSONRenderer
from UserManagement.utils import get_and_authenticate_user, create_user_account
from UserManagement import serializers as sz
import json
from django.core import serializers

# assuming obj is a model instance


User = User()


@api_view(('POST',))
@permission_classes([])
@authentication_classes([])
@csrf_exempt
def validate_mobile(request):
    serializer = sz.UserLoginSerializer(data= json.loads(request.body))
    if serializer.is_valid():
        user = create_user_account(**serializer.data)
        serialized_obj = serializers.serialize('json', [ user[0], ])
        print(serialized_obj)
        data = sz.AuthBrokersUserserializer(user[0]).data
        if user[1]:
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(('POST',))
@csrf_exempt
def validate_otp(request):
    print(request)
    serializer = serializers.AuthBrokersUserserializer(data=request.data)
    print(serializer)
    if serializer.is_valid(raise_exception=True):
        user = get_and_authenticate_user(**serializer.validated_data)
        data = serializers.AuthBrokersUserserializer().get_auth_token.data
        if user:
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


    

# class AuthViewSet(viewsets.GenericViewSet):
#     permission_classes = [AllowAny, ]
#     serializer_class = serializers.EmptySerializer
#     serializer_classes = {
#         'login': serializers.UserLoginSerializer,
#         'register': serializers.UserRegisterSerializer
#     }

#     @action(methods=['POST', ], detail=False)
#     def login(self, request):
#         ...

#     @action(methods=['POST', ], detail=False)
#     def register(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = create_user_account(**serializer.validated_data)
#         data = serializers.AuthBrokersUserserializer(user).data
#         return Response(data=data, status=status.HTTP_201_CREATED)
    

#     @action(methods=['POST', ], detail=False)
#     def logout(self, request):
#         logout(request)
#         data = {'success': 'Sucessfully logged out'}
#         return Response(data=data, status=status.HTTP_200_OK)

#     def get_serializer_class(self):
#         ...