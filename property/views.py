from rest_framework.generics import ListAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework import status
from django.views.generic import View

from property.estate.estate_serializers import EstateSerializer
from property.models import Estate
from django.shortcuts import render
from property.models import Broker
from UserManagement.models import User
from property.location.location_serializers import BrokerDetailSerializer
from property.utils import ReturnJsonResponse


# Create your views here.

class Broker_Page(View):
    def get(self, *args, **kwargs):
        try:
            mobile = kwargs.get("mobile")
            print(mobile)
            user = User.objects.get(mobile=mobile)
            queryset = Broker.objects.get(mobile=user.mobile)
            serializer = BrokerDetailSerializer(queryset,context= {"user":user})
            print(serializer.data)
            return render(self.request, "property/index.html", serializer.data)
            
        except Exception as e:
            return ReturnJsonResponse(errors=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            #messages.info(self.request, "You do not have an active order")

class ListEstateAPIView(ListAPIView):
    """This endpoint list all of the available todos from the database"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class CreateEstateAPIView(CreateAPIView):
    """This endpoint allows for creation of a todo"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class UpdateEstateAPIView(UpdateAPIView):
    """This endpoint allows for updating a specific todo by passing in the id of the todo to update"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

class DeleteEstateAPIView(DestroyAPIView):
    """This endpoint allows for deletion of a specific Estate from the database"""
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer


