from dataclasses import fields
from rest_framework import serializers
from property.models import City,Area,Apartment, Broker ,Estate
from UserManagement.models import BrokersUsers
from chat.models import Contacts


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        exclude = ["is_deleted"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ["is_deleted"]


class BrokerSerializer(serializers.ModelSerializer):
    area = serializers.ListField(
            child=serializers.CharField(max_length = 1000)
            )
    estate_type = serializers.ListField(
            child=serializers.CharField(max_length = 1000)
            )
    class Meta:
        model = Broker
        exclude = ["mobile"]

class BrokerDetailSerializer(serializers.ModelSerializer):
    contacts = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    estates = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    estate_type = serializers.SerializerMethodField()
     
    class Meta:
        model = Broker
        fields = ["name","mobile","balance","contacts","estates","area","estate_type"]
    def get_contacts(self,obj):
        if "request" in self.context:
            request = self.context["request"]
            return len(Contacts.objects.filter(owner = request.user.mobile))
        else:
            user = self.context["user"]
            return len(Contacts.objects.filter(owner = user.mobile))

    def get_estates(self,obj):
        if "request" in self.context:
            request = self.context["request"]
            return len(Estate.objects.filter(broker_mobile = request.user.mobile))
        else:
            user = self.context["user"]
            return Estate.objects.filter(broker_mobile = user.mobile)

    def get_balance(self,obj):
        if "request" in self.context:
            request = self.context["request"]
            return request.user.balance
        else:
            user = self.context["user"]
            return user.balance
    def get_area(self,obj):
        if obj.area:
            return str(obj.area).split(",")
        else:
            return []
    def get_estate_type(self,obj):
        if obj.estate_type:
            return str(obj.estate_type).split(",")
        else:
            return []
        

    
       
class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        exclude = ["is_deleted"]


class ApartmentlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ["area"]

class ApartmentbulkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ["apartment_name","area"]