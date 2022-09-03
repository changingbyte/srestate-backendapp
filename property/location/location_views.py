from ast import Return
import imp
import re
from urllib.parse import quote_from_bytes
from UserManagement.models import User
from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import UpdateAPIView
# from rest_framework.generics import DetailAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view ,authentication_classes, permission_classes
import pymongo
from srestate.settings import mongo_uri 
from srestate.config import CACHES
import json
import redis
from property.utils import ReturnJsonResponse, ReturnResponse
from property.location.location_serializers import ApartmentbulkSerializer, BrokerSerializer, CitySerializer, AreaSerializer, ApartmentSerializer ,ApartmentlistSerializer,BrokerDetailSerializer
from property.models import Area, Broker,City, Apartment


cache = redis.Redis(
    host=CACHES["default"]["host"],
    port=CACHES["default"]["port"], 
    password=CACHES["default"]["password"])
POOL = redis.ConnectionPool(host= CACHES["default"]["host"], port=CACHES["default"]["port"], db=0)
r = redis.StrictRedis(connection_pool=POOL)

print(mongo_uri)
client = pymongo.MongoClient(mongo_uri)
db = client['your-db-name']

# Create your views here.
class ListCityAPIView(ListAPIView):
    queryset = City.objects.filter(is_deleted = 0)
    serializer_class = CitySerializer

class CreateCityAPIView(CreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class UpdateCityAPIView(UpdateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class DeleteCityAPIView(DestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class ListAreaAPIView(ListAPIView):
    serializer_class = AreaSerializer
    def get(self,request):
        mycol = db.property_area
        queryset = mycol.find({"is_deleted":False})
        if "area" in cache:
            areas = cache.get("area")
            areas = json.loads(areas)
            data  = areas
        else:
            serializer = AreaSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name= "area", value=jobject, time=60*60*24)
            data = serializer.data
        return ReturnResponse(data=data, success=True, status=status.HTTP_200_OK)

class CreateAreaAPIView(CreateAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

    def post(self,request):
        serializer = AreaSerializer(data=request.data)
        try:
            if serializer.is_valid():

                area,created = Area.objects.get_or_create(
                    area_name = serializer.data["area_name"],
                    city = City.objects.get(pk=serializer.data["city"]),
                    pincode = serializer.data["pincode"]
                )
                area.save()

                return ReturnResponse(success=True,msg="Created Successfully", status=status.HTTP_200_OK)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateAreaAPIView(UpdateAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    def put(self,request,**kwargs):
        serializer = AreaSerializer(data=request.data)
        id = kwargs.get('pk',0)
        try:
            if serializer.is_valid():
                try:
                    area = Area.objects.get(pk = id)
                    area.area_name = serializer.data["area_name"]
                    area.city = City.objects.get(pk=serializer.data["city"])
                    area.pincode = serializer.data["pincode"]
                    area.save()

                    return ReturnResponse(success=True,msg="Updated Successfully", status=status.HTTP_200_OK)
                except Exception as e:
                    return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAreaAPIView(DestroyAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    def delete(self,request,**kwargs):
        id = kwargs.get('pk',0)
        try:
            area = Area.objects.get(pk = id)
            area.is_deleted = True
            area.save()

            context = {
                "msg":"Deleted Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        except Area.DoesNotExist:
            context = {
                "msg": "Record Does Not Exists"
            }

            return Response(context, status=status.HTTP_200_OK)







class ListApartmentAPIView(ListAPIView):
    queryset = Apartment.objects.filter(is_deleted = 0)
    serializer_class = ApartmentlistSerializer
    def get(self,request):
        try:
            client = pymongo.MongoClient(mongo_uri)
            db = client['your-db-name']
            mycol = db.property_apartment
            if "area" in request.data:
                cache_key = "area_"+str(request.data["area"])
                if cache_key in cache:
                    areas = cache.get(cache_key)
                    areas = json.loads(areas)
                    data  = areas
                else:
                    queryset = mycol.find({"is_deleted":False,"area": {"$in":request.data["area"]}})
                    serializer = ApartmentSerializer(queryset,many = True)
                    jobject = json.dumps(serializer.data)
                    cache.setex(name= cache_key, value=jobject, time=60*60*24)
                    data = serializer.data
            else:
                queryset = mycol.find({"is_deleted":False})
                serializer = ApartmentSerializer(queryset,many = True)
                data = serializer.data
        
            return ReturnResponse(success=True,data=data, status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateBulkApartmentAPIView(CreateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentbulkSerializer

    def post(self,request):
        context = []
        apartmentlist = request.data["apartmentlist"]
        for data in apartmentlist:
            print(data)
            apartment,created = Apartment.objects.get_or_create(
                apartment_name = data["apartment_name"].lower(),
                area = data["area"].lower()
            )
            apartment.save()

            context.append({
                "msg":"Created Successfully"
            })
        

            
        
        return Response(context, status=status.HTTP_200_OK)


class CreateBrokerAPIView(CreateAPIView):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer

    def post(self,request):
        try:
            serializer = BrokerSerializer(data=request.data)
            if serializer.is_valid():
            
                    mycol = db.property_broker
                    updatestmt = (
                        {"mobile":request.user.mobile},
                        {"$set":{
                            "name": serializer.data["name"],
                            "area": ",".join(serializer.data["area"]),
                            "estate_type": ",".join(serializer.data["estate_type"]),
                        }}
                    )
                    broker = mycol.update_one(*updatestmt)
                    if broker.raw_result["n"] == 0:
                        updatestmt = (
                        {"mobile":request.user.mobile},
                        {"$set":{
                            "name": serializer.data["name"],
                            "area": ",".join(serializer.data["area"]),
                            "estate_type": ",".join(serializer.data["estate_type"]),
                        }}
                        )
                        broker = mycol.update_one(
                            *updatestmt, upsert= True)
                        mycol = db.UserManagement_user
                        updatestmt = (
                            {"mobile":request.user.mobile},
                            {"$set":{
                                "balance": 1000,
                                "is_profile_completed":True
                            }}
                        )
                        broker = mycol.update_one(*updatestmt)
                        msg="Created Successfully"
                        return ReturnResponse(success=True,msg=msg, status=status.HTTP_201_CREATED)
                    else:
                        msg = "Updated Successfully"
                        return ReturnResponse(success=True,msg=msg, status=status.HTTP_200_OK)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
@api_view(('GET',))
def get_broker_profile(request) :
    try:
        queryset = Broker.objects.get(mobile=request.user.mobile)
        serializer = BrokerDetailSerializer(queryset,context= {"request":request})
        return ReturnJsonResponse(data=serializer.data,success=True,msg="Profile Details",status=status.HTTP_200_OK )
    except Exception as e:
        return ReturnJsonResponse(errors=str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(('GET',))
def get_balance(request):
    context = {"balance":request.user.balance}
    return ReturnResponse(success=True,data=context, status=status.HTTP_200_OK)
    

class CreateApartmentAPIView(CreateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer

    def post(self,request):
        try:
            serializer = ApartmentSerializer(data=request.data)
            if serializer.is_valid():
                apartment,created = Apartment.objects.get_or_create(
                    apartment_name = serializer.data["apartment_name"],
                    area = Area.objects.get(pk=serializer.data["area"]),
                )
                apartment.save()

                return ReturnResponse(success=True,msg="Created Successfully", status=status.HTTP_200_OK)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)
        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateApartmentAPIView(UpdateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    def put(self,request,**kwargs):
        try:
            serializer = ApartmentSerializer(data=request.data)
            id = kwargs.get('pk',0)
            if serializer.is_valid():
                try:
                    apartment = Apartment.objects.get(pk = id)
                    apartment.apartment_name = serializer.data["apartment_name"]
                    apartment.area = Area.objects.get(pk=serializer.data["area"])
                    apartment.save()

                    return ReturnResponse(success=True,msg="Updated Successfully", status=status.HTTP_200_OK)
                except Exception as e:
                    return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return ReturnResponse(errors= serializer.errors,msg="", status=status.HTTP_200_OK)

        except Exception as e:
            return ReturnResponse(errors=str(e),msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteApartmentAPIView(DestroyAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    def delete(self,request,**kwargs):
        id = kwargs.get('pk','0')
        try:
            apartment = Apartment.objects.get(pk = id)
            apartment.is_deleted = 1
            apartment.save()

            context = {
                "msg":"Deleted Successfully"
            }

            return Response(context, status=status.HTTP_200_OK)

        except Apartment.DoesNotExist:
            context = {
                "msg": "Record Does Not Exists"
            }

            return Response(context, status=status.HTTP_200_OK)





