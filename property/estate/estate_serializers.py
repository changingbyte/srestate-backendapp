from dataclasses import fields
from email.policy import default
from typing_extensions import Required
from rest_framework import serializers
from property.models import Estate, EstateStatus, EstateType,photos,City,Apartment

class EstateCreateSerializer(serializers.ModelSerializer):
    def create(self,validate_data):
        return Estate.objects.create(**validate_data)

    class Meta:
        model = Estate
        fields = ["id","estate_name","city","estate_type","floor_space",
        "number_of_bedrooms","estate_description","estate_status", "rent_status","society",
        "area","budget","furniture"]

    def get_estate_name(self,obj):
        if obj['floor_space'] and obj['number_of_bedrooms']:
            obj['estate_name'] = f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['floor_space']}sqft {obj['area']} {obj['society']}"
            return f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['floor_space']}sqft {obj['area']} {obj['society']}"
        elif obj['floor_space']:
            obj['estate_name'] =  f"{obj['estate_type']} {obj['estate_status']} {obj['floor_space']}sqft {obj['area']} {obj['society']}"
            return f"{obj['estate_type']} {obj['estate_status']} {obj['floor_space']}sqft {obj['area']} {obj['society']}"
        elif obj['number_of_bedrooms']:
            obj['estate_name'] =  f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['area']} {obj['society']}"
            return f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['area']} {obj['society']}"
        else:
            obj['estate_name'] =  f"{obj['estate_type']} {obj['estate_status']}  {obj['area']} {obj['society']}"
            return f"{obj['estate_type']} {obj['estate_status']}  {obj['area']} {obj['society']}"



class EstateSerializer(serializers.ModelSerializer):
    is_my_property = serializers.SerializerMethodField()
    def create(self,validate_data):
        return Estate.objects.create(**validate_data)
    

    class Meta:
        model = Estate
        fields = ["id","estate_name","is_my_property","city","estate_type","floor_space",
        "number_of_bedrooms","estate_description","estate_status", "rent_status","society",
        "area","budget","furniture" ,"broker_mobile","broker_name"]

    def get_is_my_property(self,obj):
        if "request" in self.context:
            request = self.context["request"]
            if obj["broker_mobile"] == request.user.mobile:
                return True
            return False
        return False


class EsateRealtedObjectSerilaizer(serializers.Serializer):
    id = serializers.IntegerField()
    estate_name = serializers.CharField()
    city = serializers.CharField()
    estate_type = serializers.CharField()
    furniture = serializers.CharField()
    floor_space = serializers.SerializerMethodField()
    number_of_bedrooms = serializers.IntegerField()
    estate_description = serializers.CharField()
    estate_status = serializers.CharField()
    rent_status = serializers.CharField(allow_blank=True)
    is_deleted = serializers.BooleanField()
    society = serializers.CharField()
    area = serializers.CharField()
    broker_mobile = serializers.CharField()
    broker_name = serializers.CharField(allow_blank=True)
    budget = serializers.IntegerField()
    is_my_property = serializers.SerializerMethodField()

    class Meta:
        fields = ["id","estate_name","is_my_property","city","estate_type","floor_space",
        "number_of_bedrooms","estate_description","estate_status", "rent_status","society",
        "area","budget","furniture" ,"broker_mobile","broker_name"]

    def get_is_my_property(self,obj):
        if "request" in self.context:
            request = self.context["request"]
            if obj["broker_mobile"] == request.user.mobile:
                return True
            return False
        return False
    
    def get_floor_space(self,obj):
        if "floor_space" in obj:
            return str(obj["floor_space"])
        return "0"


class EstateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateStatus
        exclude = ['is_deleted']


class EstateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateType
        fields = ["type_name" ]


class ImageSerializer(serializers.ModelSerializer):

    def create(self,validate_data):
        return photos.objects.create(**validate_data)

    class Meta:
        model = photos
        fields = '__all__'


class EstateWPSerializer(serializers.Serializer):
    string = serializers.CharField()
    #mobile  = serializers.CharField(max_length = 10)